"""Tests for the ontology-native compliance lookup module + its MCP tool wrapper.

CONCEPT:LP-OS.governance.legal-compliance-kb. Covers ``compliance_kb.run_action``
directly and the ``handle_compliance_lookup`` MCP handler, including the honest
degrade-without-rdflib path.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("rdflib")

# `compliance_kb` is pure stdlib + rdflib (no agent_utilities dependency), so it's
# imported at module level; `mcp_compliance` pulls in agent_utilities for logging,
# so its import is deferred into the two handler tests below that specifically
# need it — keeping the rest of this file collectible even in an environment where
# agent_utilities itself is mid-refactor/broken (see AGENTS.md's pre-authorized
# `agent_utilities-MCPAgent` skip).
from legal_peripherals_mcp import compliance_kb


@pytest.mark.concept("LEGAL-002")
def test_list_domains_includes_all_domain_and_compliance_modules():
    domains = compliance_kb.run_action("list_domains")
    iris = {d["iri"] for d in domains}
    assert "http://knuckles.team/kg/legal-compliance" in iris
    assert "http://knuckles.team/kg/legal-domain-employment" in iris
    assert "http://knuckles.team/kg/legal-domain-commercial" in iris
    assert "http://knuckles.team/kg/legal-domain-privacy" in iris


@pytest.mark.concept("LEGAL-002")
def test_list_regulations_filters_by_dataclass_case_insensitive_substring():
    regs = compliance_kb.run_action("list_regulations", data_class="phi")
    ids = {r["id"] for r in regs}
    assert "HIPAA" in ids


@pytest.mark.concept("LEGAL-002")
def test_regulation_detail_returns_obligations_and_controls():
    detail = compliance_kb.run_action("regulation_detail", regulation="FLSA")
    assert detail["id"] == "FLSA"
    obligation_ids = {o["id"] for o in detail["obligations"]}
    assert "FLSAOvertimeObligation" in obligation_ids
    overtime = next(
        o for o in detail["obligations"] if o["id"] == "FLSAOvertimeObligation"
    )
    assert any(c["id"] == "FLSATimekeepingControl" for c in overtime["controls"])


@pytest.mark.concept("LEGAL-002")
def test_regulation_detail_unknown_regulation_raises():
    with pytest.raises(compliance_kb.ComplianceLookupError):
        compliance_kb.run_action("regulation_detail", regulation="NotARealRegulation")


@pytest.mark.concept("LEGAL-002")
def test_sector_lookup_requires_sector():
    with pytest.raises(compliance_kb.ComplianceLookupError):
        compliance_kb.run_action("sector_lookup")


@pytest.mark.concept("LEGAL-002")
def test_gate_requirements_resolves_multiple_regulations_and_controls():
    result = compliance_kb.run_action("gate_requirements", data_classes="PHI,PII")
    assert "HIPAA" in result["applicable_regulations"]
    assert "ePHI Encryption Control" in result["required_controls"]


@pytest.mark.concept("LEGAL-002")
def test_unknown_action_raises():
    with pytest.raises(compliance_kb.ComplianceLookupError):
        compliance_kb.run_action("not_a_real_action")


@pytest.mark.concept("LEGAL-002")
def test_graph_without_rdflib_reports_honest_unavailability(monkeypatch):
    """Mirrors the fleet's honest-unavailability convention (see mcp_sos.py) — a
    missing optional dependency degrades to a clear notice, never a fabricated
    answer or a wall of traceback."""
    compliance_kb._graph.cache_clear()
    import builtins

    real_import = builtins.__import__

    def _blocked_import(name, *args, **kwargs):
        if name == "rdflib":
            raise ImportError("no rdflib in this environment")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked_import)
    with pytest.raises(
        compliance_kb.ComplianceLookupError, match="rdflib is not installed"
    ):
        compliance_kb.run_action("list_domains")
    compliance_kb._graph.cache_clear()


@pytest.mark.concept("LEGAL-002")
@pytest.mark.asyncio
async def test_handle_compliance_lookup_returns_result_dict():
    from legal_peripherals_mcp.mcp.mcp_compliance import handle_compliance_lookup

    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()
    res = await handle_compliance_lookup(action="list_domains", ctx=mock_ctx)
    assert "result" in res
    assert res["action"] == "list_domains"


@pytest.mark.concept("LEGAL-002")
@pytest.mark.asyncio
async def test_handle_compliance_lookup_returns_error_not_raise():
    from legal_peripherals_mcp.mcp.mcp_compliance import handle_compliance_lookup

    res = await handle_compliance_lookup(action="regulation_detail", regulation="")
    assert res["action"] == "regulation_detail"
    assert "error" in res
