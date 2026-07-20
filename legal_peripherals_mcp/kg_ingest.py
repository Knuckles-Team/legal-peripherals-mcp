"""Native epistemic-graph ingestion for legal-peripherals records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. This package natively pushes its
data into the ONE epistemic-graph knowledge graph as **typed OWL nodes** — Secretary
-of-State business entities (``:BusinessEntity`` + ``:Jurisdiction``) and IRS EIN
applications (``:EINApplication``) — plus the text of drafted filings / statute
summaries as ``:Document`` nodes for semantic search. Raw filing files (drafts) go in
as blobs via :mod:`legal_peripherals_mcp.kg_media`.

Everything rides the required
``agent_utilities.knowledge_graph.memory.native_ingest`` authority. Node ids follow
``legal:<class>:<externalId>`` and every ``node_type`` matches a class the package's
``ontology`` federates.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any

from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_documents as _native_ingest_documents,
)
from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_entities as _native_ingest_entities,
)

logger = logging.getLogger("legal_peripherals_mcp.kg")

_SOURCE = "legal-peripherals-mcp"
_DOMAIN = "legal"

# OpenCorporates config mirrors legal_peripherals_mcp.mcp.mcp_sos so the wire-first
# ingest tool queries the exact same real registry aggregator.
_OC_BASE_URL = os.getenv(
    "OPENCORPORATES_BASE_URL", "https://api.opencorporates.com/v0.4"
).rstrip("/")
_OC_TIMEOUT = int(os.getenv("SOS_TIMEOUT_SECONDS", "30"))




def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write typed OWL nodes (+ edges) into epistemic-graph. See module docstring."""
    return _native_ingest_entities(
        entities,
        relationships,
        source=source,
        domain=domain,
        client=client,
        graph=graph,
    )


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write text records as ``:Document`` nodes (semantic-search fodder)."""
    return _native_ingest_documents(
        documents, source=source, domain=domain, client=client, graph=graph
    )


# --------------------------------------------------------------------------- #
# Mappers: record → typed entity/document dicts.
# --------------------------------------------------------------------------- #
def _slug(value: str) -> str:
    """A stable, id-safe slug for a free-text key (e.g. a legal name)."""
    return (
        re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
        or "unknown"
    )


def ingest_sos_entities(
    companies: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
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
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_ein_application(
    legal_name: str,
    *,
    trade_name: str = "",
    business_type: str = "",
    county_state: str = "",
    reason_for_applying: str = "",
    closing_month_tax_year: str = "",
    filing_status: str = "",
    draft_text: str = "",
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Map a drafted IRS SS-4 → ``:EINApplication`` (+ ``:BusinessEntity``) nodes."""
    if not (legal_name or "").strip():
        return ingest_entities([], client=client, graph=graph)
    slug = _slug(legal_name)
    aid = f"legal:einapplication:{slug}"
    bid = f"legal:businessentity:{slug}"
    entities = [
        {
            "id": aid,
            "node_type": "EINApplication",
            "name": f"SS-4: {legal_name}",
            "legal_name": legal_name,
            "trade_name": trade_name or None,
            "business_type": business_type or None,
            "filingType": "ss4_ein",
            "filingAgency": "IRS",
            "filingStatus": filing_status or None,
            "county_state": county_state or None,
            "reason_for_applying": reason_for_applying or None,
            "closing_month_tax_year": closing_month_tax_year or None,
            "text": draft_text or None,
            "externalToolId": slug,
        },
        {
            "id": bid,
            "node_type": "BusinessEntity",
            "name": legal_name,
            "company_type": business_type or None,
        },
    ]
    relationships = [
        {"source": aid, "target": bid, "relationship": "appliesForEntity"}
    ]
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_filing_document(
    doc_id: str,
    text: str,
    *,
    title: str = "",
    doc_type: str = "legal_document",
    source_uri: str = "",
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Store a rendered filing / statute summary as a searchable ``:Document`` node."""
    if not doc_id or not (text or "").strip():
        return ingest_documents([], client=client, graph=graph)
    doc: dict[str, Any] = {"id": doc_id, "text": text, "doc_type": doc_type}
    if title:
        doc["title"] = title
    if source_uri:
        doc["source_uri"] = source_uri
    return ingest_documents([doc], client=client, graph=graph)


# --------------------------------------------------------------------------- #
# Wire-first fetch: live OpenCorporates search for the ingest MCP tool.
# --------------------------------------------------------------------------- #
def search_companies(
    state: str,
    entity_name: str,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """List real OpenCorporates company records for a state + name (best-effort).

    Returns ``[]`` when no ``OPENCORPORATES_API_TOKEN`` is set or the request fails,
    so the source query returns no records rather than fabricating data. Native
    ingestion remains authoritative whenever records are available.
    """
    token = os.getenv("OPENCORPORATES_API_TOKEN", "").strip()
    if not token or not (state or "").strip() or not (entity_name or "").strip():
        return []
    jurisdiction = f"us_{state.strip().lower()}"
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
