"""Native epistemic-graph ingestion for legal-peripherals records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. This package natively pushes its
data into the ONE epistemic-graph knowledge graph as **typed OWL nodes** — Secretary
-of-State business entities (``:BusinessEntity`` + ``:Jurisdiction``) and IRS EIN
applications (``:EINApplication``) — plus the text of drafted filings / statute
summaries as ``:Document`` nodes for semantic search. Raw filing files (drafts) go in
as blobs via :mod:`legal_peripherals_mcp.kg_media`.

Everything rides the **lightweight engine client** (``GraphComputeEngine()._client`` +
``txn``) through the shared ``agent_utilities...native_ingest`` primitive. The primitive
import is GUARDED: when the shared helper is not present in the installed agent_utilities,
this module falls back to a self-contained txn writer with the identical contract. Either
way the whole seam is dependency-/engine-guarded — with no KG stack or no reachable engine
every entry point **no-ops** (returns ``None``), so the connector runs with zero KG
infrastructure. Node ids follow ``legal:<class>:<externalId>`` and every ``type`` matches a
class the package's ``ontology`` federates.
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Any

logger = logging.getLogger("legal_peripherals_mcp.kg")

_SOURCE = "legal-peripherals-mcp"
_DOMAIN = "legal"
_DEFAULT_GRAPH = "__commons__"

# OpenCorporates config mirrors legal_peripherals_mcp.mcp.mcp_sos so the wire-first
# ingest tool queries the exact same real registry aggregator.
_OC_BASE_URL = os.getenv(
    "OPENCORPORATES_BASE_URL", "https://api.opencorporates.com/v0.4"
).rstrip("/")
_OC_TIMEOUT = int(os.getenv("SOS_TIMEOUT_SECONDS", "30"))


# --------------------------------------------------------------------------- #
# Write path: shared primitive with a self-contained fallback.
# --------------------------------------------------------------------------- #
try:  # Preferred: the fleet's one push-into-the-KG path.
    from agent_utilities.knowledge_graph.memory.native_ingest import (
        ingest_documents as _shared_ingest_documents,
    )
    from agent_utilities.knowledge_graph.memory.native_ingest import (
        ingest_entities as _shared_ingest_entities,
    )

    _HAVE_SHARED = True
except Exception as e:  # noqa: BLE001 — primitive not yet in installed agent_utilities
    logger.debug("native_ingest primitive unavailable, using fallback: %s", e)
    _HAVE_SHARED = False


def _fallback_client() -> tuple[Any | None, str]:
    """Resolve ``(engine_client, graph)`` via the lightweight engine, or ``(None, "")``."""
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        return client, (getattr(engine, "graph_name", None) or _DEFAULT_GRAPH)
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("KG ingest: engine unreachable: %s", e)
        return None, ""


def _fallback_write_nodes(
    nodes: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None,
    *,
    client: Any | None,
    graph: str | None,
) -> dict[str, int] | None:
    """Self-contained txn writer, contract-identical to the shared primitive."""
    nodes = [n for n in (nodes or []) if n.get("id")]
    if not nodes:
        return None
    if client is None:
        client, graph = _fallback_client()
    if client is None:
        return None
    graph = graph or _DEFAULT_GRAPH
    try:
        txn = client.txn.begin(graph=graph)
        for node in nodes:
            props = {k: v for k, v in node.items() if k != "id" and v is not None}
            props.setdefault("source", _SOURCE)
            props.setdefault("domain", _DOMAIN)
            client.txn.add_node(txn, node["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("KG ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("KG ingest: txn not committed (conflict)")
        return None
    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("KG ingest: edge skipped: %s", e)
    logger.info("KG ingest: wrote %d nodes, %d edges", len(nodes), edges)
    return {"nodes": len(nodes), "edges": edges}


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed OWL nodes (+ edges) into epistemic-graph. See module docstring."""
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None
    if _HAVE_SHARED and client is None:
        return _shared_ingest_entities(
            entities, relationships, source=source, domain=domain
        )
    return _fallback_write_nodes(entities, relationships, client=client, graph=graph)


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write text records as ``:Document`` nodes (semantic-search fodder)."""
    docs = [
        d
        for d in (documents or [])
        if d.get("id") and (d.get("text") or d.get("content"))
    ]
    if not docs:
        return None
    if _HAVE_SHARED and client is None:
        return _shared_ingest_documents(docs, source=source, domain=domain)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    nodes: list[dict[str, Any]] = []
    for doc in docs:
        node = {k: v for k, v in doc.items() if k != "content" and v is not None}
        node["id"] = doc["id"]
        node["type"] = "Document"
        node["text"] = doc.get("text") or doc.get("content")
        node.setdefault("created_at", now)
        nodes.append(node)
    return _fallback_write_nodes(nodes, None, client=client, graph=graph)


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
) -> dict[str, int] | None:
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
                "type": "BusinessEntity",
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
                    "type": "Jurisdiction",
                    "name": company.get("jurisdiction_code"),
                }
            )
            relationships.append(
                {"source": eid, "target": jid, "type": "incorporatedIn"}
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
) -> dict[str, int] | None:
    """Map a drafted IRS SS-4 → ``:EINApplication`` (+ ``:BusinessEntity``) nodes."""
    if not (legal_name or "").strip():
        return None
    slug = _slug(legal_name)
    aid = f"legal:einapplication:{slug}"
    bid = f"legal:businessentity:{slug}"
    entities = [
        {
            "id": aid,
            "type": "EINApplication",
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
            "type": "BusinessEntity",
            "name": legal_name,
            "company_type": business_type or None,
        },
    ]
    relationships = [{"source": aid, "target": bid, "type": "appliesForEntity"}]
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
) -> dict[str, int] | None:
    """Store a rendered filing / statute summary as a searchable ``:Document`` node."""
    if not doc_id or not (text or "").strip():
        return None
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
    so the wire-first ingest tool degrades to a no-op rather than fabricating data.
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
                "per_page": max(1, min(int(limit), 100)),
            },
            timeout=_OC_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:  # noqa: BLE001 — live fetch is best-effort
        logger.warning("SOS company search failed: %s", e)
        return []
    results = (payload.get("results") or {}).get("companies") or []
    return [c.get("company", c) for c in results if c]
