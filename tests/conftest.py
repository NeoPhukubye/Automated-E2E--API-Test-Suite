import pytest
from utils.api_client import APIClient


@pytest.fixture(scope="session")
def api():
    """Provide a shared API client instance for the test session."""
    return APIClient()
