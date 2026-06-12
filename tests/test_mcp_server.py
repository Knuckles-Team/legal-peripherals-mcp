from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.concept("LEGAL-002")
def test_mcp_server_registration():
    """CONCEPT:LEGAL-002 Test that tools register successfully."""
    from legal_peripherals_mcp.mcp_server import get_mcp_instance

    mcp, _args, _middlewares = get_mcp_instance()
    assert mcp is not None

    # Verify tool registry count is greater than zero
    assert len(mcp._local_provider._components) > 0


@pytest.mark.concept("LEGAL-002")
@pytest.mark.asyncio
async def test_mcp_tools_routing():
    """Verify that all tools route correctly."""
    from legal_peripherals_mcp.mcp_server import get_mcp_instance

    mcp, _args, _middlewares = get_mcp_instance()

    # Extract registered tools from _components dict values
    tools = {t.name: t for t in mcp._local_provider._components.values()}
    assert "sos_entity_lookup" in tools
    assert "draft_ein_form" in tools
    assert "lookup_statute_rules" in tools

    # Mock context
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    # Test sos_entity_lookup for TX — with no API token configured it must
    # report unavailability honestly and fabricate NO record.
    tx_res = await tools["sos_entity_lookup"].fn(
        state="TX", entity_name="Antigravity LLC", ctx=mock_ctx
    )
    assert "TX" in tx_res
    assert "unavailable" in tx_res.lower()
    assert "none was fabricated" in tx_res

    # Same honest behavior for a non-primary state.
    ca_res = await tools["sos_entity_lookup"].fn(
        state="CA", entity_name="Antigravity LLC", ctx=mock_ctx
    )
    assert "CA" in ca_res
    assert "unavailable" in ca_res.lower()

    # Test draft_ein_form scheduling or instant filing
    ein_res = await tools["draft_ein_form"].fn(
        legal_name="Antigravity LLC",
        trade_name="Antigravity",
        responsible_party_ssn="123-45-6789",
        responsible_party_name="John Doe",
        business_type="LLC",
        mailing_address="123 Main St, Austin, TX 78701",
        county_state="Travis, TX",
        reason_for_applying="Started new business",
        first_date_wages_paid="2026-06-01",
        max_employees=5,
        closing_month_tax_year="December",
        ctx=mock_ctx,
    )
    assert "Antigravity LLC" in ein_res
    assert "SS-4 draft" in ein_res

    # Test lookup_statute_rules
    statute_res = await tools["lookup_statute_rules"].fn(
        state="DE", entity_type="Corporation", topic="voting", ctx=mock_ctx
    )
    assert "DE" in statute_res
    assert "Corporation" in statute_res
    assert "voting" in statute_res
