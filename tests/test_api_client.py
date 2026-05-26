import pytest
from unittest.mock import MagicMock, patch
from legal_peripherals_mcp.api_client import Api


@pytest.mark.concept("LEGAL-001")
def test_api_client_basic_mock(mock_ctx):
    """CONCEPT:LEGAL-001 Test basic mock initialization of client facade."""
    assert mock_ctx is not None
    assert hasattr(mock_ctx, "info")


@pytest.mark.concept("LEGAL-001")
def test_api_client_endpoints(mock_ctx):
    """CONCEPT:LEGAL-001 Verify endpoint configuration on dynamic client."""
    from legal_peripherals_mcp.auth import get_client

    client = get_client()
    assert client is not None
    assert hasattr(client, "request")


@pytest.mark.concept("LEGAL-001")
def test_api_client_full_endpoints():
    """Test the newly added endpoints with mocked HTTP sessions or responses."""
    client = Api(base_url="http://localhost:8000")

    with patch.object(client._session, "request") as mock_request:
        # Mock successful JSON response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"status": "success"}
        mock_request.return_value = mock_response

        # Test request
        res = client.request("GET", "/test")
        assert res == {"status": "success"}
        args, kwargs = mock_request.call_args
        assert args[0] == "GET"
        assert args[1] == "http://localhost:8000/test"
