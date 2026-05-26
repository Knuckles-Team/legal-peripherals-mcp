"""CONCEPT:LEGAL-003 Identity credentials loader and session manager."""
import os

from agent_utilities.base_utilities import get_logger, to_boolean
from legal_peripherals_mcp.api_client import Api

logger = get_logger(__name__)


def get_client() -> Api:
    """Get authenticated client for legal_peripherals_mcp."""
    base_url = os.getenv("LEGAL_PERIPHERALS_BASE_URL", "")
    token = os.getenv("LEGAL_PERIPHERALS_TOKEN", "")
    verify = to_boolean(os.getenv("LEGAL_PERIPHERALS_SSL_VERIFY", "True"))

    if not base_url:
        # Default fallback for testing
        base_url = "http://localhost:8000"

    return Api(
        base_url=base_url,
        token=token,
        verify=verify,
    )
