import pytest


@pytest.mark.concept("LEGAL-001")
def test_init_dynamics():
    import legal_peripherals_mcp

    assert legal_peripherals_mcp._MCP_AVAILABLE
