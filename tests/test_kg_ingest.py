"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the ``kg_ingest`` seam with a fake engine client (no engine required),
asserting the txn add_node/commit + edge calls and the legal record → typed-node
mappings. CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from legal_peripherals_mcp.kg_ingest import (
    ingest_documents,
    ingest_ein_application,
    ingest_entities,
    ingest_filing_document,
    ingest_sos_entities,
    search_companies,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def commit(self, txn):
        self.committed = True
        return True


class _FakeEdges:
    def __init__(self):
        self.edges = []

    def add(self, src, dst, props):
        self.edges.append((src, dst, props))


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()
        self.edges = _FakeEdges()


def test_ingest_entities_writes_nodes_and_edges_with_provenance():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "type": "BusinessEntity", "name": "Acme"},
            {"id": "b", "type": "Jurisdiction"},
        ],
        [{"source": "a", "target": "b", "type": "incorporatedIn"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    assert c.txn.nodes["a"]["source"] == "legal-peripherals-mcp"
    assert c.txn.nodes["a"]["domain"] == "legal"
    assert c.edges.edges == [("a", "b", {"type": "incorporatedIn"})]


def test_ingest_entities_empty_is_noop():
    assert ingest_entities([], client=_FakeClient()) is None


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
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    ent = c.txn.nodes["legal:businessentity:us_de_1234567"]
    assert ent["type"] == "BusinessEntity"
    assert ent["name"] == "Acme Holdings LLC"
    assert ent["companyNumber"] == "1234567"
    assert ent["registryStatus"] == "Active"
    assert ent["incorporationDate"] == "2020-01-15"
    assert ent["externalToolId"] == "us_de_1234567"
    jur = c.txn.nodes["legal:jurisdiction:us_de"]
    assert jur["type"] == "Jurisdiction"
    assert c.edges.edges == [
        (
            "legal:businessentity:us_de_1234567",
            "legal:jurisdiction:us_de",
            {"type": "incorporatedIn"},
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
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    app = c.txn.nodes["legal:einapplication:acme-holdings-llc"]
    assert app["type"] == "EINApplication"
    assert app["filingType"] == "ss4_ein"
    assert app["filingAgency"] == "IRS"
    assert app["filingStatus"] == "queued"
    assert app["text"] == "=== SS-4 ..."
    ent = c.txn.nodes["legal:businessentity:acme-holdings-llc"]
    assert ent["type"] == "BusinessEntity"
    assert c.edges.edges == [
        (
            "legal:einapplication:acme-holdings-llc",
            "legal:businessentity:acme-holdings-llc",
            {"type": "appliesForEntity"},
        )
    ]


def test_ingest_ein_application_blank_name_is_noop():
    assert ingest_ein_application("   ", client=_FakeClient()) is None


def test_ingest_documents_and_filing_document():
    c = _FakeClient()
    res = ingest_documents(
        [{"id": "legal:document:d1", "text": "hello", "doc_type": "statute_summary"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.txn.nodes["legal:document:d1"]
    assert node["type"] == "Document"
    assert node["text"] == "hello"
    assert "created_at" in node

    c2 = _FakeClient()
    res2 = ingest_filing_document(
        "legal:document:de-llc-voting",
        "State: DE ... default voting rules",
        title="DE LLC voting",
        doc_type="statute_summary",
        client=c2,
        graph="__commons__",
    )
    assert res2 == {"nodes": 1, "edges": 0}
    assert c2.txn.nodes["legal:document:de-llc-voting"]["title"] == "DE LLC voting"


def test_ingest_filing_document_empty_text_is_noop():
    assert ingest_filing_document("id", "   ", client=_FakeClient()) is None


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
