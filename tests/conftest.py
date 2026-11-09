"""Root pytest fixtures shared across API and E2E tests."""

import os
import json
from typing import Generator
from urllib.parse import urlparse, parse_qs

import pytest
import allure
import requests_mock
from utils.api_client import APIClient
from utils.test_data import DataGenerator
from config.settings import UI_BASE_URL, HEADLESS, VIEWPORT_WIDTH, VIEWPORT_HEIGHT, BASE_URL, VERIFY_SSL


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

        def _mock_get(url, request):
            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            path = parsed.path

            if path == "/products":
                limit = int(query.get("limit", [len(products)])[0])
                sort = query.get("sort", [""])[0]
                result = products[:limit]
                if sort == "desc":
                    result = list(reversed(result))
                return result
            elif path.startswith("/products/category/"):
                category = path.split("/")[-1]
                filtered = [p for p in products if p.get("category") == category]
                return filtered[:1] if filtered else [product1]
            elif path == "/products/categories":
                return categories
            elif path.startswith("/products/"):
                pid = path.split("/")[-1]
                return next((p for p in products if str(p.get("id")) == pid), product1)
            elif path == "/users":
                return users
            elif path.startswith("/users/"):
                uid = path.split("/")[-1]
                return next((u for u in users if str(u.get("id")) == uid), users[0] if users else {})
            elif path == "/carts":
                return carts
            elif path.startswith("/carts/"):
                cid = path.split("/")[-1]
                return next((c for c in carts if str(c.get("id")) == cid), carts[0] if carts else {})
            return {}

        def _mock_post(url, request):
            if "/auth/login" in url:
                return login
            elif "/products" in url:
                return {"id": 21, **product1}
            return {}

        def _mock_put(url, request):
            if "/products/" in url:
                return product1
            return {}

        def _mock_patch(url, request):
            if "/products/" in url:
                return product1
            return {}

        def _mock_delete(url, request):
            if "/products/" in url:
                return product1
            return {}

        requests_mock.get(requests_mock.ANY, json=_mock_get)
        requests_mock.post(requests_mock.ANY, json=_mock_post)
        requests_mock.put(requests_mock.ANY, json=_mock_put)
        requests_mock.patch(requests_mock.ANY, json=_mock_patch)
        requests_mock.delete(requests_mock.ANY, json=_mock_delete)

        yield
    else:
        yield


@pytest.fixture(scope="session")
def base_url() -> str:
    """Provide the base API URL from settings."""
    return BASE_URL


@pytest.fixture
def valid_credentials() -> dict:
    """Provide valid login credentials for FakeStore API."""
    return {"username": "mor_2314", "password": "83r5^_"}