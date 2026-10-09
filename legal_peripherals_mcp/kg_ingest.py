"""Epistemic-graph ingestion for legal-peripherals records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. This package pushes its data into
the ONE epistemic-graph knowledge graph as **typed OWL nodes** — Secretary-of-State
business entities (``:BusinessEntity`` + ``:Jurisdiction``) and IRS EIN applications
(``:EINApplication``) — plus the text of drafted filings / statute summaries as
``:Document`` nodes for semantic search. Raw filing files (drafts) go in as blobs via
:mod:`legal_peripherals_mcp.kg_media`.

Everything rides ``agent_connector_sdk.ingest`` -- the generated ``SourceIngest``
client, not a local ingestion helper. Node ids follow ``legal:<class>:<externalId>``
and every ``node_type`` matches a class the package's ``ontology`` federates.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any

from agent_connector_sdk.ingest import (
    ChangeSet,
    Document,
    Entity,
    IngestBinding,
    IngestError,
    KnowledgeIngest,
    Relationship,
    current_ingest,
)

logger = logging.getLogger("legal_peripherals_mcp.kg")

_SOURCE = "legal-peripherals-mcp"
_DOMAIN = "legal"

_BINDING = IngestBinding(connector=_SOURCE, stream=_DOMAIN)

_ENTITY_RESERVED_KEYS = frozenset({"id", "node_type"})
_RELATIONSHIP_RESERVED_KEYS = frozenset({"source", "target", "relationship"})

# OpenCorporates config mirrors legal_peripherals_mcp.mcp.mcp_sos so the wire-first
# ingest tool queries the exact same real registry aggregator.
_OC_BASE_URL = os.getenv(
    "OPENCORPORATES_BASE_URL", "https://api.opencorporates.com/v0.4"
).rstrip("/")
_OC_TIMEOUT = int(os.getenv("SOS_TIMEOUT_SECONDS", "30"))


def _to_entity(record: dict[str, Any]) -> Entity:
    return Entity(
        id=record.get("id"),
        node_type=record.get("node_type"),
        properties={
            key: value
            for key, value in record.items()
            if key not in _ENTITY_RESERVED_KEYS
        },
    )


def _to_relationship(record: dict[str, Any]) -> Relationship:
    properties = {
        key: value
        for key, value in record.items()
        if key not in _RELATIONSHIP_RESERVED_KEYS
    }
    return Relationship(
        source=record["source"],
        target=record["target"],
        relationship=record["relationship"],
        properties=properties or None,
    )


async def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write typed OWL nodes (+ edges) into epistemic-graph. See module docstring."""
    if not entities:
        raise IngestError("ingest_entities needs at least one entity")
    change_set = ChangeSet(
        entities=tuple(_to_entity(entity) for entity in entities or ()),
        relationships=tuple(
            _to_relationship(relationship) for relationship in relationships or ()
        ),
    )
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


async def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write text records as ``:Document`` nodes (semantic-search fodder)."""
    if not documents:
        raise IngestError("ingest_documents needs at least one document")
    change_set = ChangeSet(
        documents=tuple(
            Document(
                id=doc["id"],
                text=doc["text"],
                title=doc.get("title"),
                source_uri=doc.get("source_uri"),
                properties={
                    key: value
                    for key, value in doc.items()
                    if key not in {"id", "text", "title", "source_uri"}
                },
            )
            for doc in documents or ()
        )
    )
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


# --------------------------------------------------------------------------- #
# Mappers: record → typed entity/document dicts.
# --------------------------------------------------------------------------- #
def _slug(value: str) -> str:
    """A stable, id-safe slug for a free-text key (e.g. a legal name)."""
    return (
        re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
        or "unknown"
    )


async def ingest_sos_entities(
    companies: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Map OpenCorporates company records → ``:BusinessEntity`` (+ ``:Jurisdiction``) nodes.

    ``companies``: OpenCorporates ``company`` dicts (``name``, ``jurisdiction_code``,
    ``company_number``, ``company_type``, ``current_status``, ``incorporation_date`` …).
    """
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for company in companies or []:
        jur = (company.get("jurisdiction_code") or "").strip().lower()
        number = str(company.get("company_number") or "").strip()
        ext = f"{jur}_{number}" if jur and number else _slug(company.get("name") or "")
        eid = f"legal:businessentity:{ext}"
        entities.append(
            {
                "id": eid,
                "node_type": "BusinessEntity",
                "name": company.get("name"),
                "jurisdiction_code": company.get("jurisdiction_code"),
                "companyNumber": number or None,
                "company_type": company.get("company_type"),
                "registryStatus": company.get("current_status"),
                "incorporationDate": company.get("incorporation_date"),
                "dissolution_date": company.get("dissolution_date"),
                "registered_address": company.get("registered_address_in_full"),
                "source_uri": company.get("opencorporates_url"),
                "externalToolId": ext,
            }
        )
        if jur:
            jid = f"legal:jurisdiction:{jur}"
            entities.append(
                {
                    "id": jid,
                    "node_type": "Jurisdiction",
                    "name": company.get("jurisdiction_code"),
                }
            )
            relationships.append(
                {"source": eid, "target": jid, "relationship": "incorporatedIn"}
            )
    return await ingest_entities(entities, relationships, ingest=ingest)


def _optional(value: str) -> str | None:
    """Normalize an empty/absent string field to ``None`` for graph ingestion."""
    return value or None


def _ein_application_entities(
    legal_name: str, aid: str, bid: str, slug: str, fields: dict[str, str]
) -> list[dict[str, Any]]:
    """Build the ``:EINApplication`` + ``:BusinessEntity`` node dicts for one filing."""
    return [
        {
            "id": aid,
            "node_type": "EINApplication",
            "name": f"SS-4: {legal_name}",
            "legal_name": legal_name,
            "trade_name": _optional(fields["trade_name"]),
            "business_type": _optional(fields["business_type"]),
            "filingType": "ss4_ein",
            "filingAgency": "IRS",
            "filingStatus": _optional(fields["filing_status"]),
            "county_state": _optional(fields["county_state"]),
            "reason_for_applying": _optional(fields["reason_for_applying"]),
            "closing_month_tax_year": _optional(fields["closing_month_tax_year"]),
            "text": _optional(fields["draft_text"]),
            "externalToolId": slug,
        },
        {
            "id": bid,
            "node_type": "BusinessEntity",
            "name": legal_name,
            "company_type": _optional(fields["business_type"]),
        },
    ]


async def ingest_ein_application(
    legal_name: str,
    *,
    trade_name: str = "",
    business_type: str = "",
    county_state: str = "",
    reason_for_applying: str = "",
    closing_month_tax_year: str = "",
    filing_status: str = "",
    draft_text: str = "",
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Map a drafted IRS SS-4 → ``:EINApplication`` (+ ``:BusinessEntity``) nodes."""
    if not (legal_name or "").strip():
        return await ingest_entities([], ingest=ingest)
    slug = _slug(legal_name)
    aid = f"legal:einapplication:{slug}"
    bid = f"legal:businessentity:{slug}"
    fields = {
        "trade_name": trade_name,
        "business_type": business_type,
        "county_state": county_state,
        "reason_for_applying": reason_for_applying,
        "closing_month_tax_year": closing_month_tax_year,
        "filing_status": filing_status,
        "draft_text": draft_text,
    }
    entities = _ein_application_entities(legal_name, aid, bid, slug, fields)
    relationships = [{"source": aid, "target": bid, "relationship": "appliesForEntity"}]
    return await ingest_entities(entities, relationships, ingest=ingest)


async def ingest_filing_document(
    doc_id: str,
    text: str,
    *,
    title: str = "",
    doc_type: str = "legal_document",
    source_uri: str = "",
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Store a rendered filing / statute summary as a searchable ``:Document`` node."""
    if not doc_id or not (text or "").strip():
        return await ingest_documents([], ingest=ingest)
    doc: dict[str, Any] = {"id": doc_id, "text": text, "doc_type": doc_type}
    if title:
        doc["title"] = title
    if source_uri:
        doc["source_uri"] = source_uri
    return await ingest_documents([doc], ingest=ingest)


# --------------------------------------------------------------------------- #
# Wire-first fetch: live OpenCorporates search for the ingest MCP tool.
# --------------------------------------------------------------------------- #
def _missing_search_inputs(token: str, state: str, entity_name: str) -> bool:
    return not token or not (state or "").strip() or not (entity_name or "").strip()


def _fetch_opencorporates_companies(
    jurisdiction: str, entity_name: str, token: str, limit: int
) -> list[dict[str, Any]]:
    """Best-effort live OpenCorporates company search; ``[]`` on any failure."""
    try:
        import requests

        resp = requests.get(
            f"{_OC_BASE_URL}/companies/search",
            params={
                "q": entity_name.strip(),
                "jurisdiction_code": jurisdiction,
                "api_token": token,
                "per_page": str(max(1, min(int(limit), 100))),
            },
            timeout=_OC_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:  # noqa: BLE001 — live fetch is best-effort
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
        return []
    results = (payload.get("results") or {}).get("companies") or []
    return [c.get("company", c) for c in results if c]


def search_companies(
    state: str,
    entity_name: str,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """List real OpenCorporates company records for a state + name (best-effort).

    Returns ``[]`` when no ``OPENCORPORATES_API_TOKEN`` is set or the request fails,
    so the source query returns no records rather than fabricating data. Ingestion
    remains authoritative whenever records are available.
    """
    token = os.getenv("OPENCORPORATES_API_TOKEN", "").strip()
    if _missing_search_inputs(token, state, entity_name):
        return []
    jurisdiction = f"us_{state.strip().lower()}"
    return _fetch_opencorporates_companies(jurisdiction, entity_name, token, limit)
