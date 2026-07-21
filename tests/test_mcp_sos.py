from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import requests

from legal_peripherals_mcp.mcp.mcp_sos import handle_sos_lookup


def _mock_response(payload):
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json = MagicMock(return_value=payload)
    return resp


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_sos_lookup_not_configured_returns_honest_notice(monkeypatch):
    """With no API token, no record is fabricated — an honest notice is returned."""
    monkeypatch.delenv("OPENCORPORATES_API_TOKEN", raising=False)
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    res = await handle_sos_lookup("TX", "Acme LLC", ctx=mock_ctx)

    assert "unavailable" in res.lower()
    assert "OPENCORPORATES_API_TOKEN" in res
    assert "none was fabricated" in res
    # No fabricated status/standing leaks through.
    assert "Good Standing" not in res
    assert "Active" not in res


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_sos_lookup_real_search_hits(monkeypatch):
    """A configured token drives a real OpenCorporates search; results are rendered."""
    monkeypatch.setenv("OPENCORPORATES_API_TOKEN", "tok_test")
    payload = {
        "results": {
            "companies": [
                {
                    "company": {
                        "name": "ACME LLC",
                        "company_number": "0123456789",
                        "jurisdiction_code": "us_de",
                        "current_status": "Good Standing",
                        "incorporation_date": "2020-01-15",
                        "company_type": "Limited Liability Company",
                        "registered_address_in_full": "1209 Orange St, Wilmington, DE",
                        "opencorporates_url": "https://opencorporates.com/companies/us_de/0123456789",
                    }
                }
            ]
        }
    }
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    with patch("legal_peripherals_mcp.mcp.mcp_sos.requests.get") as mget:
        mget.return_value = _mock_response(payload)
        res = await handle_sos_lookup("DE", "Acme LLC", ctx=mock_ctx)

    # Real call shape: search endpoint, correct jurisdiction + token.
    args, kwargs = mget.call_args
    assert args[0].endswith("/companies/search")
    assert kwargs["params"]["jurisdiction_code"] == "us_de"
    assert kwargs["params"]["api_token"] == "tok_test"
    assert kwargs["params"]["q"] == "Acme LLC"
    # Rendered real data, with verifiable provenance.
    assert "ACME LLC" in res
    assert "0123456789" in res
    assert "opencorporates.com" in res
    assert "OpenCorporates" in res


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_sos_lookup_direct_by_company_number(monkeypatch):
    """An entity_id drives a direct company fetch, not a search."""
    monkeypatch.setenv("OPENCORPORATES_API_TOKEN", "tok_test")
    payload = {
        "results": {
            "company": {
                "name": "WIDGETS INC",
                "company_number": "WY-99",
                "jurisdiction_code": "us_wy",
                "current_status": "Active",
            }
        }
    }
    with patch("legal_peripherals_mcp.mcp.mcp_sos.requests.get") as mget:
        mget.return_value = _mock_response(payload)
        res = await handle_sos_lookup("WY", "Widgets Inc", "WY-99")

    args, _ = mget.call_args
    assert args[0].endswith("/companies/us_wy/WY-99")
    assert "WIDGETS INC" in res


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_sos_lookup_no_results(monkeypatch):
    """An empty result set yields an honest 'no record found' — not a fabrication."""
    monkeypatch.setenv("OPENCORPORATES_API_TOKEN", "tok_test")
    with patch("legal_peripherals_mcp.mcp.mcp_sos.requests.get") as mget:
        mget.return_value = _mock_response({"results": {"companies": []}})
        res = await handle_sos_lookup("CA", "Nonexistent Co", ctx=None)

    assert "No Secretary-of-State record found" in res
    assert "CA" in res


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_sos_lookup_http_error_is_truthful(monkeypatch):
    """A failed request surfaces a truthful error, never fabricated data."""
    monkeypatch.setenv("OPENCORPORATES_API_TOKEN", "tok_test")
    with patch("legal_peripherals_mcp.mcp.mcp_sos.requests.get") as mget:
        mget.side_effect = requests.ConnectionError("boom")
        res = await handle_sos_lookup("NV", "Acme LLC", ctx=None)

    assert res.startswith("Error:")
    # Security hardening: the returned error is generic (no internal exception
    # detail leaked) — but it is still a truthful failure, never a fabricated record.
    assert "entity lookup failed" in res
    assert "Good Standing" not in res
    assert "Active" not in res


@pytest.mark.concept("LEGAL-001")
@pytest.mark.asyncio
async def test_sos_lookup_invalid_state():
    """Validation still rejects bad state codes."""
    res = await handle_sos_lookup("ZZ", "Acme LLC")
    assert res.startswith("Error:")
    # Bad input is still rejected; the message is generic (security hardening does
    # not echo which specific field failed validation).
    assert "invalid entity lookup parameters" in res
