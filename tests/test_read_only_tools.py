"""Read-only lookup tools (CONN-LEGAL-PERIPHERALS-MCP-R001)."""

import asyncio

import pytest

from legal_peripherals_mcp.mcp_server import get_mcp_instance

pytestmark = pytest.mark.spec("CONN-LEGAL-PERIPHERALS-MCP-R001")

READ_ONLY_TOOLS = {
    "legal_list_statute_coverage",
    "lookup_statute_rules",
    "sos_entity_lookup",
    "legal_compliance_lookup",
}


def _tools(monkeypatch):
    monkeypatch.setattr("sys.argv", ["legal-peripherals-mcp"])
    mcp, *_ = get_mcp_instance()
    return mcp, {tool.name: tool for tool in asyncio.run(mcp.list_tools())}


def test_lookups_are_listed_read_only(monkeypatch):
    _, tools = _tools(monkeypatch)
    for name in READ_ONLY_TOOLS:
        assert tools[name].annotations.read_only_hint is True, name
        assert tools[name].annotations.destructive_hint is False, name
    assert (
        tools["draft_ein_form"].annotations is None
        or not tools["draft_ein_form"].annotations.read_only_hint
    )


def test_statute_coverage_takes_no_arguments_and_lists_sources(monkeypatch):
    mcp, tools = _tools(monkeypatch)
    assert not (tools["legal_list_statute_coverage"].parameters or {}).get("required")
    result = asyncio.run(mcp.call_tool("legal_list_statute_coverage", {}))
    coverage = result.structured_content
    assert {"state": "DE", "entity_type": "LLC"} in coverage["specific_rules"]
    assert "voting" in coverage["topics"] and "template" not in coverage["topics"]
    assert "TX" in coverage["states"]
