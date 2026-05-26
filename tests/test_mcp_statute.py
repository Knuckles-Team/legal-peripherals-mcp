import pytest
from unittest.mock import MagicMock, AsyncMock

from legal_peripherals_mcp.mcp.mcp_statute import handle_statute_rules

@pytest.mark.concept("LEGAL-003")
@pytest.mark.asyncio
async def test_handle_statute_rules_delaware_corporation():
    """Verify statutory rules and templates for Delaware Corporations."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    # Test voting topic
    res_voting = await handle_statute_rules("DE", "Corporation", "voting", ctx=mock_ctx)
    assert "State: DE" in res_voting
    assert "Entity Type: Corporation" in res_voting
    assert "Topic: voting" in res_voting
    assert "DGCL Sec. 212" in res_voting
    assert "DELAWARE CERTIFICATE OF INCORPORATION TEMPLATE" in res_voting

    # Test indemnification topic
    res_indem = await handle_statute_rules("DE", "Corporation", "indemnification", ctx=mock_ctx)
    assert "DGCL Sec. 145" in res_indem


@pytest.mark.concept("LEGAL-003")
@pytest.mark.asyncio
async def test_handle_statute_rules_texas_llc():
    """Verify statutory rules and templates for Texas LLCs."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    # Test capital_contributions topic
    res_contrib = await handle_statute_rules("TX", "LLC", "capital_contributions", ctx=mock_ctx)
    assert "State: TX" in res_contrib
    assert "Entity Type: LLC" in res_contrib
    assert "Topic: capital_contributions" in res_contrib
    assert "BOC Sec. 101.151" in res_contrib
    assert "TEXAS LLC COMPANY AGREEMENT TEMPLATE" in res_contrib


@pytest.mark.concept("LEGAL-003")
@pytest.mark.asyncio
async def test_handle_statute_rules_fallback():
    """Verify statutory rule fallback for other states."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    # Test New York (NY) LLC fallback
    res = await handle_statute_rules("NY", "LLC", "voting", ctx=mock_ctx)
    assert "State: NY" in res
    assert "Entity Type: LLC" in res
    assert "Topic: voting" in res
    assert "General Fallback Statute Lookup (NY LLC)" in res
    assert "GENERAL NY LLC OPERATING AGREEMENT" in res
