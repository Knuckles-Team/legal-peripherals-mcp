"""CONCEPT:LP-OS.governance.legal Dynamic client facade orchestration and resource mappings."""

import requests
from agent_utilities.base_utilities import get_logger

logger = get_logger(__name__)


class Api:
    def __init__(self, base_url="http://localhost:8000", token="", verify=True):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.verify = verify
        self._session = requests.Session()

    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = kwargs.get("headers", {})

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        kwargs["headers"] = headers
        kwargs["verify"] = self.verify

        logger.info(f"Making request: {method} {url}")
        response = self._session.request(method, url, **kwargs)
        response.raise_for_status()

        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        return response.text
