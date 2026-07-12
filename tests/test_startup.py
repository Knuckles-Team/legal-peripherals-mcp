import re

import pytest


@pytest.mark.concept("LEGAL-001")
def test_startup():
    # Basic import test
    import legal_peripherals_mcp

    # Match a semver string rather than a hardcoded literal so this test doesn't drift
    # out of sync with .bumpversion.cfg-driven releases.
    assert re.fullmatch(r"\d+\.\d+\.\d+", legal_peripherals_mcp.__version__)
