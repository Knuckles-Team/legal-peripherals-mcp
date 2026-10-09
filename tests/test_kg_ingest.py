"""Epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the ``kg_ingest`` seam against a fake transport one level below the SDK's
own ``SourceIngest`` request builder (per the fleet SDK migration recipe), asserting
the committed nodes/edges and the legal record → typed-node mappings.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest

from legal_peripherals_mcp.kg_ingest import (
    ingest_documents,
    ingest_ein_application,
    ingest_entities,
    ingest_filing_document,
    ingest_sos_entities,
    search_companies,
)


class _FakeTransport:
    def __init__(self) -> None:
        self.requests: list[Any] = []

    async def source_status(self, connector: str, stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request: Any) -> Any:
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
        )

    async def store_blob(self, data: bytes) -> str:
        raise AssertionError("this connector's node/document ingestion carries no media")


@pytest.fixture
def ingest() -> tuple[KnowledgeIngest, _FakeTransport]:
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


def _node(transport: _FakeTransport, node_id: str) -> dict[str, Any]:
    for request in transport.requests:
        for record in request.records:
            if record.record_id == node_id:
                return dict(record.payload)
    raise AssertionError(f"no committed record {node_id!r}")


def _edges(transport: _FakeTransport) -> set[tuple[str, str, str]]:
    edges: set[tuple[str, str, str]] = set()
    for request in transport.requests:
        for rel in request.relationships:
            relationship_name = rel.relation_reference.rsplit("/relations/", 1)[-1]
            edges.add((rel.source.record_id, rel.target.record_id, relationship_name))
    return edges


@pytest.mark.asyncio
async def test_ingest_entities_writes_nodes_and_edges_with_provenance(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "BusinessEntity", "name": "Acme"},
            {"id": "b", "node_type": "Jurisdiction"},
        ],
        [{"source": "a", "target": "b", "relationship": "incorporatedIn"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    record_ids = {record.record_id for record in transport.requests[0].records}
    assert record_ids == {"a", "b"}
    assert _edges(transport) == {("a", "b", "incorporatedIn")}


@pytest.mark.asyncio
async def test_ingest_empty_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_entities([], ingest=service)


@pytest.mark.asyncio
async def test_ingest_sos_entities_maps_business_entity_and_jurisdiction(ingest):
    service, transport = ingest
    res = await ingest_sos_entities(
        [
            {
                "name": "Acme Holdings LLC",
                "jurisdiction_code": "us_de",
                "company_number": "1234567",
                "company_type": "LLC",
                "current_status": "Active",
                "incorporation_date": "2020-01-15",
                "registered_address_in_full": "1 Main St, Dover, DE",
                "opencorporates_url": "https://opencorporates.com/companies/us_de/1234567",
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    ent = _node(transport, "legal:businessentity:us_de_1234567")
    assert ent["name"] == "Acme Holdings LLC"
    assert ent["companyNumber"] == "1234567"
    assert ent["registryStatus"] == "Active"
    assert ent["incorporationDate"] == "2020-01-15"
    assert ent["externalToolId"] == "us_de_1234567"
    jur = _node(transport, "legal:jurisdiction:us_de")
    assert jur["name"] == "us_de"
    assert _edges(transport) == {
        (
            "legal:businessentity:us_de_1234567",
            "legal:jurisdiction:us_de",
            "incorporatedIn",
        )
    }


@pytest.mark.asyncio
async def test_ingest_ein_application_maps_filing_and_entity(ingest):
    service, transport = ingest
    res = await ingest_ein_application(
        "Acme Holdings LLC",
        business_type="LLC",
        county_state="Kent, DE",
        filing_status="queued",
        draft_text="=== SS-4 ...",
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    app = _node(transport, "legal:einapplication:acme-holdings-llc")
    assert app["filingType"] == "ss4_ein"
    assert app["filingAgency"] == "IRS"
    assert app["filingStatus"] == "queued"
    assert app["text"] == "=== SS-4 ..."
    ent = _node(transport, "legal:businessentity:acme-holdings-llc")
    assert ent["name"] == "Acme Holdings LLC"
    assert _edges(transport) == {
        (
            "legal:einapplication:acme-holdings-llc",
            "legal:businessentity:acme-holdings-llc",
            "appliesForEntity",
        )
    }


@pytest.mark.asyncio
async def test_ingest_ein_application_blank_name_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_ein_application("   ", ingest=service)


@pytest.mark.asyncio
async def test_ingest_documents_and_filing_document(ingest):
    service, transport = ingest
    res = await ingest_documents(
        [{"id": "legal:document:d1", "text": "hello", "doc_type": "statute_summary"}],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    node = _node(transport, "legal:document:d1")
    assert node["text"] == "hello"

    res2 = await ingest_filing_document(
        "legal:document:de-llc-voting",
        "State: DE ... default voting rules",
        title="DE LLC voting",
        doc_type="statute_summary",
        ingest=service,
    )
    assert res2 == {"nodes": 1, "edges": 0}
    assert _node(transport, "legal:document:de-llc-voting")["title"] == "DE LLC voting"


@pytest.mark.asyncio
async def test_ingest_filing_document_empty_text_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="at least one document"):
        await ingest_filing_document("id", "   ", ingest=service)


def test_search_companies_no_token_returns_empty(monkeypatch):
    monkeypatch.delenv("OPENCORPORATES_API_TOKEN", raising=False)
    assert search_companies("DE", "Acme") == []


def test_search_companies_missing_state_or_name_returns_empty(monkeypatch):
    monkeypatch.setenv("OPENCORPORATES_API_TOKEN", "tok")
    assert search_companies("", "Acme") == []
    assert search_companies("DE", "") == []


def test_search_companies_request_failure_returns_empty(monkeypatch):
    monkeypatch.setenv("OPENCORPORATES_API_TOKEN", "tok")

    import legal_peripherals_mcp.kg_ingest as kg

    class _FailingRequests:
        @staticmethod
        def get(url, params=None, timeout=None):
            raise ConnectionError("boom")

    monkeypatch.setitem(__import__("sys").modules, "requests", _FailingRequests)
    assert kg.search_companies("DE", "Acme") == []


def test_search_companies_parses_records(monkeypatch):
    monkeypatch.setenv("OPENCORPORATES_API_TOKEN", "tok")

    class _Resp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "results": {
                    "companies": [
                        {"company": {"name": "Acme", "company_number": "1"}},
                        {"company": {"name": "Acme 2", "company_number": "2"}},
                    ]
                }
            }

    import legal_peripherals_mcp.kg_ingest as kg

    class _FakeRequests:
        @staticmethod
        def get(url, params=None, timeout=None):
            assert params["jurisdiction_code"] == "us_de"
            return _Resp()

    monkeypatch.setitem(__import__("sys").modules, "requests", _FakeRequests)
    out = kg.search_companies("DE", "Acme", limit=5)
    assert [c["name"] for c in out] == ["Acme", "Acme 2"]
