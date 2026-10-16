"""Root pytest fixtures shared across API and E2E tests."""

import os
import json

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


def _load_fixture(name):
    p = os.path.join(os.path.dirname(__file__), "fixtures", f"{name}.json")
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(autouse=True)
def mock_external_api(requests_mock):
    """Mock external API calls in CI environments."""
    if os.getenv("GITHUB_ACTIONS", "").lower() in ("true",) or os.getenv("CI", "").lower() in ("true",):
        base = os.getenv("BASE_URL", "https://fakestoreapi.com")
        products = _load_fixture("products")
        users = _load_fixture("users")
        carts = _load_fixture("carts")
        product1 = products[0] if products else _load_fixture("product_1")
        login = _load_fixture("login")
        categories = _load_fixture("categories")

        # GET requests
        requests_mock.get(f"{base}/products", json=products)
        requests_mock.get(f"{base}/products/category/electronics", json=[product1])
        requests_mock.get(f"{base}/products/category/jewelry", json=[products[1] if len(products) > 1 else product1])
        requests_mock.get(f"{base}/products/categories", json=categories)
        requests_mock.get(f"{base}/products/1", json=product1)
        requests_mock.get(f"{base}/products/2", json=products[1] if len(products) > 1 else product1)
        requests_mock.get(f"{base}/users", json=users)
        requests_mock.get(f"{base}/users/1", json=users[0] if users else {})
        requests_mock.get(f"{base}/users/2", json=users[0] if users else {})
        requests_mock.get(f"{base}/carts", json=carts)
        requests_mock.get(f"{base}/carts/1", json=carts[0] if carts else {})

        # Query param variants
        requests_mock.get(
            f"{base}/products?limit=5",
            json=[products[0], products[1] if len(products) > 1 else products[0], products[0], products[1] if len(products) > 1 else products[0], products[0]],
        )
        requests_mock.get(f"{base}/products?sort=desc", json=list(reversed(products)))
        requests_mock.get(f"{base}/products?limit=2&sort=asc", json=products[:2])

        # POST/PATCH/PUT/DELETE
        requests_mock.post(f"{base}/auth/login", json=login, status_code=200)
        requests_mock.post(f"{base}/products", json={"id": 21, **product1}, status_code=201)
        requests_mock.put(f"{base}/products/1", json=product1, status_code=200)
        requests_mock.patch(f"{base}/products/1", json=product1, status_code=200)
        requests_mock.delete(f"{base}/products/1", json=product1, status_code=200)

        yield
    else:
        yield