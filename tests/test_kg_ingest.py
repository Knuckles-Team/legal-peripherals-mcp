"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the ``kg_ingest`` seam with a ChangeEnvelope-capable fake engine client
(no engine required), asserting the native node/edge writes and the legal record →
typed-node mappings. CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.models.company_brain import ActorType
from agent_utilities.security.brain_context import ActorContext, use_actor

from legal_peripherals_mcp.kg_ingest import (
    ingest_documents,
    ingest_ein_application,
    ingest_entities,
    ingest_filing_document,
    ingest_sos_entities,
    search_companies,
)


@pytest.fixture(autouse=True)
def _governed_session():
    """Bind the verified ambient GraphSession the native-ingest path requires.

    ``kg_ingest`` delegates to ``agent_utilities`` native ingestion, whose
    ``resolve_session(required_scope="kg:write")`` refuses to run without an
    ambient authenticated session. Mirror agent-utilities' own native-ingest
    test setup so these fake-client tests exercise the real ingest path.
    """
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.AUTOMATED_SERVICE,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="graph:opaque:synthetic",
        policy_version="policy:opaque:synthetic",
        audience="epistemic-graph",
    )
    with use_actor(actor), use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    """ChangeEnvelope-capable fake: unpacks the applied envelope the way the
    engine would, so the tests can assert the written nodes/edges. Mirrors
    agent-utilities' own native-ingest test double."""

    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


def test_ingest_entities_writes_nodes_and_edges_with_provenance():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "BusinessEntity", "name": "Acme"},
            {"id": "b", "node_type": "Jurisdiction"},
        ],
        [{"source": "a", "target": "b", "relationship": "incorporatedIn"}],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(c.changes.applied) >= 1
    assert set(c.nodes.values) == {"a", "b"}
    assert c.nodes.values["a"]["source"] == "legal-peripherals-mcp"
    assert c.nodes.values["a"]["domain"] == "legal"
    assert c.changes.edges == [("a", "b", {"relationship": "incorporatedIn"})]


def test_ingest_empty_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())


def test_ingest_sos_entities_maps_business_entity_and_jurisdiction():
    c = _FakeClient()
    res = ingest_sos_entities(
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
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    ent = c.nodes.values["legal:businessentity:us_de_1234567"]
    assert ent["node_type"] == "BusinessEntity"
    assert ent["name"] == "Acme Holdings LLC"
    assert ent["companyNumber"] == "1234567"
    assert ent["registryStatus"] == "Active"
    assert ent["incorporationDate"] == "2020-01-15"
    assert ent["externalToolId"] == "us_de_1234567"
    jur = c.nodes.values["legal:jurisdiction:us_de"]
    assert jur["node_type"] == "Jurisdiction"
    assert c.changes.edges == [
        (
            "legal:businessentity:us_de_1234567",
            "legal:jurisdiction:us_de",
            {"relationship": "incorporatedIn"},
        )
    ]


def test_ingest_ein_application_maps_filing_and_entity():
    c = _FakeClient()
    res = ingest_ein_application(
        "Acme Holdings LLC",
        business_type="LLC",
        county_state="Kent, DE",
        filing_status="queued",
        draft_text="=== SS-4 ...",
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    app = c.nodes.values["legal:einapplication:acme-holdings-llc"]
    assert app["node_type"] == "EINApplication"
    assert app["filingType"] == "ss4_ein"
    assert app["filingAgency"] == "IRS"
    assert app["filingStatus"] == "queued"
    assert app["text"] == "=== SS-4 ..."
    ent = c.nodes.values["legal:businessentity:acme-holdings-llc"]
    assert ent["node_type"] == "BusinessEntity"
    assert c.changes.edges == [
        (
            "legal:einapplication:acme-holdings-llc",
            "legal:businessentity:acme-holdings-llc",
            {"relationship": "appliesForEntity"},
        )
    ]


def test_ingest_ein_application_blank_name_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_ein_application("   ", client=_FakeClient())


def test_ingest_documents_and_filing_document():
    c = _FakeClient()
    res = ingest_documents(
        [{"id": "legal:document:d1", "text": "hello", "doc_type": "statute_summary"}],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.nodes.values["legal:document:d1"]
    assert node["node_type"] == "Document"
    assert node["text"] == "hello"
    # Native authoritative ingestion stamps provenance on every node (the
    # bitemporal timestamp lives on the ChangeEnvelope/content-version, not as a
    # node-level ``created_at`` property).
    assert node["source"] == "legal-peripherals-mcp"
    assert node["domain"] == "legal"

    c2 = _FakeClient()
    res2 = ingest_filing_document(
        "legal:document:de-llc-voting",
        "State: DE ... default voting rules",
        title="DE LLC voting",
        doc_type="statute_summary",
        client=c2,
    )
    assert res2 == {"nodes": 1, "edges": 0}
    assert c2.nodes.values["legal:document:de-llc-voting"]["title"] == "DE LLC voting"


def test_ingest_filing_document_empty_text_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one document"):
        ingest_filing_document("id", "   ", client=_FakeClient())


def test_search_companies_no_token_returns_empty(monkeypatch):
    monkeypatch.delenv("OPENCORPORATES_API_TOKEN", raising=False)
    assert search_companies("DE", "Acme") == []


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
