import pytest


@pytest.fixture(autouse=True)
def _isolate_live_kg_ingest(monkeypatch):
    """Disable default-on native KG ingestion for the unit suite.

    The MCP tools (`mcp_sos`, `mcp_ein`, ...) ingest their results into the
    epistemic-graph by default, and that ingestion is authoritative — a failure
    propagates rather than being swallowed. No engine is reachable in the unit
    environment, so leaving ingestion on would make every draft/lookup test fail
    on `NativeIngestError` instead of exercising its own logic. Turn it off via
    the public `LEGAL_KG_INGEST` knob so the tool tests stay hermetic; production
    behavior (authoritative ingestion when an engine is present) is unchanged.

    Tests that exercise the ingestion primitives directly
    (`tests/test_kg_ingest.py`) call them with a fake client and do not consult
    this flag, so they are unaffected.
    """
    monkeypatch.setenv("LEGAL_KG_INGEST", "false")


@pytest.fixture
def mock_ctx():
    class MockCtx:
        def info(self, msg):
            pass

        def warn(self, msg):
            pass

        def error(self, msg):
            pass

    return MockCtx()
