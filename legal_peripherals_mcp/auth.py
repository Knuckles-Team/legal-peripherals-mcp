"""CONCEPT:LP-OS.identity.legal Identity credentials loader and session manager."""

from agent_connector_sdk.utilities import get_logger
from agent_connector_sdk.config import setting

from legal_peripherals_mcp.api_client import Api

logger = get_logger(__name__)


def get_client() -> Api:
    """Get authenticated client for legal_peripherals_mcp."""
    base_url = setting("LEGAL_PERIPHERALS_BASE_URL", "")
    token = setting("LEGAL_PERIPHERALS_TOKEN", "")
    if not base_url:
        # Default fallback for testing
        base_url = "http://localhost:8000"

    return Api(
        base_url=base_url,
        token=token,
    )
