import pytest
from unittest.mock import MagicMock, AsyncMock

from legal_peripherals_mcp.mcp.mcp_sos import handle_sos_lookup

@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_handle_sos_lookup_texas():
    """Verify Texas Secretary of State lookup."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()
    
    res = await handle_sos_lookup("TX", "Acme LLC", ctx=mock_ctx)
    assert "Texas Secretary of State" in res
    assert "Acme LLC" in res
    assert "Registered Agent: Antigravity Agent Services LLC" in res


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_handle_sos_lookup_delaware():
    """Verify Delaware Secretary of State lookup."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()
    
    res = await handle_sos_lookup("DE", "Acme Corp", "DE-12345", ctx=mock_ctx)
    assert "Delaware Division of Corporations" in res
    assert "Acme Corp" in res
    assert "File Number: DE-12345" in res


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_handle_sos_lookup_wyoming():
    """Verify Wyoming Secretary of State lookup."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()
    
    res = await handle_sos_lookup("WY", "Acme LLC", ctx=mock_ctx)
    assert "Wyoming Secretary of State" in res
    assert "Acme LLC" in res
    assert "Limited Liability Company" in res


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_handle_sos_lookup_nevada():
    """Verify Nevada Secretary of State lookup."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()
    
    res = await handle_sos_lookup("NV", "Acme LLC", ctx=mock_ctx)
    assert "Nevada SilverFlume" in res
    assert "Acme LLC" in res


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_handle_sos_lookup_fallback():
    """Verify the structured resilient LLM fallback crawler for other states."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()
    
    # Test California (CA) fallback
    res = await handle_sos_lookup("CA", "Acme LLC", ctx=mock_ctx)
    assert "Resilient Fallback Secretary of State Lookup (CA)" in res
    assert "Acme LLC" in res
    assert "LLM fallback crawler" in res
