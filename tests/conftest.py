"""Root pytest fixtures shared across API and E2E tests."""

import pytest
import allure
from utils.api_client import APIClient
from utils.test_data import DataGenerator
from config.settings import UI_BASE_URL, HEADLESS, VIEWPORT_WIDTH, VIEWPORT_HEIGHT


class ResponseStoringAPIClient:
    """Wrapper around APIClient that stores the last response on the test node.

    Enables Allure reporting to attach response details (status code, body)
    when API tests fail, which is essential for debugging 403 errors and
    JSON parsing failures in CI environments.
    """

    def __init__(self, client: APIClient, request):
        self._client = client
        self._request = request

    def _store(self, response):
        self._request.node.last_response = response
        return response

    def get(self, endpoint: str, **kwargs):
        return self._store(self._client.get(endpoint, **kwargs))

    def post(self, endpoint: str, json=None, **kwargs):
        return self._store(self._client.post(endpoint, json=json, **kwargs))

    def put(self, endpoint: str, json=None, **kwargs):
        return self._store(self._client.put(endpoint, json=json, **kwargs))

    def patch(self, endpoint: str, json=None, **kwargs):
        return self._store(self._client.patch(endpoint, json=json, **kwargs))

    def delete(self, endpoint: str, **kwargs):
        return self._store(self._client.delete(endpoint, **kwargs))

    def close(self) -> None:
        self._client.close()

    @property
    def base_url(self):
        return self._client.base_url

    @property
    def session(self):
        return self._client.session


@pytest.fixture
def api(request):
    """Provide an API client that stores responses for Allure reporting."""
    client = APIClient()
    yield ResponseStoringAPIClient(client, request)
    client.close()


@pytest.fixture(scope="session")
def fake() -> DataGenerator:
    """Provide a shared DataGenerator instance for the test session."""
    return DataGenerator()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure Playwright browser launch options from settings."""
    return {**browser_type_launch_args, "headless": HEADLESS}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure Playwright browser context with base URL and viewport."""
    return {
        **browser_context_args,
        "base_url": UI_BASE_URL,
        "viewport": {"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
    }


@pytest.fixture(autouse=True)
def attach_api_response(request):
    """Attach API response details to Allure report on failure."""
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        if hasattr(request.node, "last_response"):
            response = request.node.last_response
            allure.attach(
                str(response.status_code),
                name="Status Code",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                response.text[:2000],
                name="Response Body",
                attachment_type=allure.attachment_type.JSON,
            )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test report on the item for fixture access."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)