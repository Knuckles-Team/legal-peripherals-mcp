import os
import zoneinfo
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from legal_peripherals_mcp.mcp.mcp_ein import (
    get_next_filing_time,
    handle_ein_draft,
    is_irs_active,
)


@pytest.mark.concept("LEGAL-002")
def test_is_irs_active():
    """Verify IRS active hours rule (Mon-Fri 7:00 AM - 10:00 PM EST)."""
    eastern = zoneinfo.ZoneInfo("America/New_York")

    # Active hours: Wednesday at 10:00 AM EST
    active_dt = datetime(2026, 5, 27, 10, 0, 0, tzinfo=eastern)
    assert is_irs_active(active_dt) is True

    # Weekend: Saturday at 10:00 AM EST
    weekend_dt = datetime(2026, 5, 30, 10, 0, 0, tzinfo=eastern)
    assert is_irs_active(weekend_dt) is False

    # Off-hours weekday: Wednesday at 11:00 PM EST
    off_hours_dt = datetime(2026, 5, 27, 23, 0, 0, tzinfo=eastern)
    assert is_irs_active(off_hours_dt) is False


@pytest.mark.concept("LEGAL-002")
def test_get_next_filing_time():
    """Verify next filing hour calculation."""
    eastern = zoneinfo.ZoneInfo("America/New_York")

    # Off-hours weekday: Wednesday at 11:00 PM EST -> next should be Thursday at 7:00 AM EST
    dt = datetime(2026, 5, 27, 23, 0, 0, tzinfo=eastern)
    next_time = get_next_filing_time(dt)
    assert next_time.weekday() == 3  # Thursday
    assert next_time.hour == 7
    assert next_time.minute == 0


@pytest.mark.concept("LEGAL-002")
@pytest.mark.asyncio
async def test_handle_ein_draft_active_hours():
    """Verify EIN drafting behavior when filing is active."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    # Force weekday daytime in Eastern zone for current datetime
    active_now = datetime(2026, 5, 27, 10, 0, 0, tzinfo=zoneinfo.ZoneInfo("UTC"))

    with patch("legal_peripherals_mcp.mcp.mcp_ein.datetime") as mock_datetime:
        mock_datetime.now.return_value = active_now
        # Patch is_irs_active directly for safety
        with patch(
            "legal_peripherals_mcp.mcp.mcp_ein.is_irs_active", return_value=True
        ):
            res = await handle_ein_draft(
                legal_name="Test LLC",
                trade_name="Testy",
                responsible_party_ssn="000-00-0000",
                responsible_party_name="Jane Doe",
                ctx=mock_ctx,
            )
            assert "Test LLC" in res
            assert "Jane Doe" in res
            assert "FILING IMMEDIATELY" in res


@pytest.mark.concept("LEGAL-002")
@pytest.mark.asyncio
async def test_handle_ein_draft_off_hours():
    """Verify EIN queuing behavior when filing is off-hours."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    off_hours_now = datetime(2026, 5, 27, 23, 0, 0, tzinfo=zoneinfo.ZoneInfo("UTC"))

    with patch("legal_peripherals_mcp.mcp.mcp_ein.datetime") as mock_datetime:
        mock_datetime.now.return_value = off_hours_now
        with patch(
            "legal_peripherals_mcp.mcp.mcp_ein.is_irs_active", return_value=False
        ):
            res = await handle_ein_draft(
                legal_name="Test LLC",
                trade_name="Testy",
                responsible_party_ssn="000-00-0000",
                responsible_party_name="Jane Doe",
                ctx=mock_ctx,
            )
            assert "Test LLC" in res
            assert "QUEUED FOR SCHEDULING" in res


@pytest.mark.concept("LEGAL-002")
@pytest.mark.asyncio
async def test_handle_ein_draft_bypass_override():
    """Verify BYPASS_IRS_FILING_HOURS=True override works perfectly."""
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    off_hours_now = datetime(2026, 5, 27, 23, 0, 0, tzinfo=zoneinfo.ZoneInfo("UTC"))

    with patch.dict(os.environ, {"BYPASS_IRS_FILING_HOURS": "True"}):
        with patch("legal_peripherals_mcp.mcp.mcp_ein.datetime") as mock_datetime:
            mock_datetime.now.return_value = off_hours_now
            with patch(
                "legal_peripherals_mcp.mcp.mcp_ein.is_irs_active", return_value=False
            ):
                res = await handle_ein_draft(legal_name="Test LLC", ctx=mock_ctx)
                assert "Test LLC" in res
                assert "FILING IMMEDIATELY" in res
