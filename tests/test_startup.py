import pytest


@pytest.mark.concept("LEGAL-001")
def test_startup():
    # Basic import test
    import legal_peripherals_mcp

    assert legal_peripherals_mcp.__version__ == "0.15.0"
