"""CONCEPT:LP-OS.governance.legal Dynamic client facade orchestration and resource mappings."""

import requests
from agent_utilities.base_utilities import get_logger
from agent_utilities.core.transport_security import (
    ResolvedTLSProfile,
    resolve_configured_tls_profile,
)

logger = get_logger(__name__)


class Api:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        token: str = "",
        tls_profile: ResolvedTLSProfile | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.tls_profile = tls_profile or resolve_configured_tls_profile(
            "legal_peripherals"
        )
        self._session = self.tls_profile.configure_requests_session(requests.Session())

    def close(self) -> None:
        """Release transport resources and runtime-only TLS material."""
        self._session.close()
        self.tls_profile.cleanup()

    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = kwargs.get("headers", {})

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        kwargs["headers"] = headers
        logger.info("Making configured legal-data request: method=%s", method)
        response = self._session.request(method, url, **kwargs)
        response.raise_for_status()

        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        return response.text
