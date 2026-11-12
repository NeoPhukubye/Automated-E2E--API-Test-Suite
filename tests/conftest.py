"""Root pytest fixtures shared across API and E2E tests."""

import os
import json
import logging
from typing import Generator, Dict, Any, List, Optional
from urllib.parse import urlparse, parse_qs
from contextlib import contextmanager

import pytest
import allure
import requests_mock as requests_mock_module
from utils.api_client import APIClient, RequestLog
from utils.test_data import DataGenerator
from config.settings import (
    UI_BASE_URL, HEADLESS, VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
    BASE_URL, VERIFY_SSL, MOCK_API, API_TIMEOUT
)


# Configure logging for test debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def head(self, endpoint: str, **kwargs):
        return self._store(self._client.head(endpoint, **kwargs))

    def options(self, endpoint: str, **kwargs):
        return self._store(self._client.options(endpoint, **kwargs))

    def close(self) -> None:
        self._client.close()

    @property
    def base_url(self):
        return self._client.base_url

    @property
    def session(self):
        return self._client.session

    def get_last_request_log(self) -> Optional[RequestLog]:
        """Get the last request log for debugging."""
        return self._client.get_last_request_log()


@pytest.fixture
def api(request):
    """Provide an API client that stores responses for Allure reporting."""
    client = APIClient(log_requests=True)
    yield ResponseStoringAPIClient(client, request)
    client.close()


@pytest.fixture
def api_client() -> APIClient:
    """Provide a raw API client without response storing wrapper.

    Useful for tests that need direct access to the client methods
    or need to inspect request logs.
    """
    client = APIClient(log_requests=True)
    yield client
    client.close()


@pytest.fixture(scope="session")
def fake() -> DataGenerator:
    """Provide a shared DataGenerator instance for the test session."""
    return DataGenerator()


@pytest.fixture
def fake_per_test() -> DataGenerator:
    """Provide a fresh DataGenerator instance per test for isolation."""
    return DataGenerator(seed=None)


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
        # Also attach request log if available
        if hasattr(request.node, "_api_client"):
            log = request.node._api_client.get_last_request_log()
            if log:
                allure.attach(
                    f"{log.method} {log.url}",
                    name="Request",
                    attachment_type=allure.attachment_type.TEXT,
                )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test report on the item for fixture access."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def _load_fixture(name: str) -> Any:
    """Load a JSON fixture file from tests/fixtures/."""
    p = os.path.join(os.path.dirname(__file__), "fixtures", f"{name}.json")
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _get_request_body(request_proxy) -> Dict[str, Any]:
    """Extract JSON body from a requests_mock _RequestObjectProxy."""
    try:
        body = request_proxy.body
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        if isinstance(body, str) and body:
            return json.loads(body)
    except Exception:
        pass
    return {}


class APIMockBuilder:
    """Builder class for creating configurable API mocks."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.products = _load_fixture("products")
        self.users = _load_fixture("users")
        self.carts = _load_fixture("carts")
        self.product1 = self.products[0] if self.products else _load_fixture("product_1")
        self.login = _load_fixture("login")
        self.categories = _load_fixture("categories")
        self._carts_state = list(self.carts)
        self._products_state = list(self.products)
        self._users_state = list(self.users)

    def _get_query(self, query: Dict[str, List[str]], name: str, default=None) -> Any:
        val = query.get(name, [default])
        return val[0] if val else default

    def _parse_url(self, url_str: str):
        parsed = urlparse(url_str)
        query = parse_qs(parsed.query)
        return parsed.path, query

    def mock_get(self, request, context):
        """Mock GET requests."""
        url_str = request.url if hasattr(request, 'url') else str(request)
        path, query = self._parse_url(url_str)

        if path == "/products":
            limit = int(self._get_query(query, "limit", len(self._products_state)))
            sort = self._get_query(query, "sort", "")
            result = list(self._products_state)
            if sort == "desc":
                result = sorted(result, key=lambda p: p["id"], reverse=True)
            elif sort == "asc":
                result = sorted(result, key=lambda p: p["id"])
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return result[:limit]

        elif path.startswith("/products/category/"):
            from urllib.parse import unquote
            category = unquote(path.split("/")[-1])
            filtered = [p for p in self._products_state if p.get("category") == category]
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return filtered if filtered else []

        elif path == "/products/categories":
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return self.categories

        elif path.startswith("/products/"):
            pid = path.split("/")[-1]
            if not pid.isdigit():
                context.status_code = 404
                context.headers["Content-Type"] = "application/json"
                return {"error": "Product not found"}
            product = next((p for p in self._products_state if str(p.get("id")) == pid), None)
            if product is None:
                context.status_code = 404
                context.headers["Content-Type"] = "application/json"
                return {"error": "Product not found"}
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return product

        elif path == "/users":
            limit = int(self._get_query(query, "limit", len(self._users_state)))
            sort = self._get_query(query, "sort", "")
            result = list(self._users_state)
            if sort == "desc":
                result = sorted(result, key=lambda u: u["id"], reverse=True)
            elif sort == "asc":
                result = sorted(result, key=lambda u: u["id"])
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return result[:limit]

        elif path.startswith("/users/"):
            uid = path.split("/")[-1]
            if not uid.isdigit():
                context.status_code = 404
                context.headers["Content-Type"] = "application/json"
                return {"error": "User not found"}
            user = next((u for u in self._users_state if str(u.get("id")) == uid), None)
            if user is None:
                context.status_code = 404
                context.headers["Content-Type"] = "application/json"
                return {"error": "User not found"}
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return user

        elif path == "/carts":
            limit = int(self._get_query(query, "limit", len(self._carts_state)))
            sort = self._get_query(query, "sort", "")
            startdate = self._get_query(query, "startdate", "")
            enddate = self._get_query(query, "enddate", "")
            result = list(self._carts_state)
            if startdate or enddate:
                result = [
                    c for c in result
                    if (not startdate or c["date"] >= startdate)
                    and (not enddate or c["date"] <= enddate)
                ]
            if sort == "desc":
                result = sorted(result, key=lambda c: c["id"], reverse=True)
            elif sort == "asc":
                result = sorted(result, key=lambda c: c["id"])
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return result[:limit]

        elif path.startswith("/carts/user/"):
            uid = path.split("/")[-1]
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return [c for c in self._carts_state if str(c.get("userId")) == uid]

        elif path.startswith("/carts/"):
            cid = path.split("/")[-1]
            if not cid.isdigit():
                context.status_code = 404
                context.headers["Content-Type"] = "application/json"
                return {"error": "Cart not found"}
            cart = next((c for c in self._carts_state if str(c.get("id")) == cid), None)
            if cart is None:
                context.status_code = 404
                context.headers["Content-Type"] = "application/json"
                return {"error": "Cart not found"}
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return cart

        context.status_code = 404
        return {"error": "Not found"}

    def mock_post(self, request, context):
        """Mock POST requests."""
        url_str = request.url if hasattr(request, 'url') else str(request)
        path, _ = self._parse_url(url_str)
        body = _get_request_body(request)

        if path == "/auth/login":
            return self.login
        elif path == "/products":
            context.status_code = 201
            context.headers["Content-Type"] = "application/json"
            new_id = max([p["id"] for p in self._products_state], default=0) + 1
            new_product = {"id": new_id, **body}
            self._products_state.append(new_product)
            return new_product
        elif path == "/users":
            context.status_code = 201
            context.headers["Content-Type"] = "application/json"
            new_id = max([u["id"] for u in self._users_state], default=0) + 1
            new_user = {"id": new_id, **body}
            self._users_state.append(new_user)
            return new_user
        elif path == "/carts":
            context.status_code = 201
            context.headers["Content-Type"] = "application/json"
            new_id = max([c["id"] for c in self._carts_state], default=0) + 1
            new_cart = {"id": new_id, **body}
            self._carts_state.append(new_cart)
            return new_cart

        context.status_code = 200
        context.headers["Content-Type"] = "application/json"
        return {}

    def mock_put(self, request, context):
        """Mock PUT requests."""
        url_str = request.url if hasattr(request, 'url') else str(request)
        path, _ = self._parse_url(url_str)
        body = _get_request_body(request)

        if path.startswith("/products/"):
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return {**self.product1, **body}
        elif path.startswith("/users/"):
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return {**self._users_state[0], **body} if self._users_state else {}
        elif path.startswith("/carts/"):
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return {**self._carts_state[0], **body} if self._carts_state else {}

        context.status_code = 200
        context.headers["Content-Type"] = "application/json"
        return {}

    def mock_patch(self, request, context):
        """Mock PATCH requests."""
        return self.mock_put(request, context)

    def mock_delete(self, request, context):
        """Mock DELETE requests."""
        url_str = request.url if hasattr(request, 'url') else str(request)
        path, _ = self._parse_url(url_str)

        if path.startswith("/products/"):
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return self.product1
        elif path.startswith("/users/"):
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return self._users_state[0] if self._users_state else {}
        elif path.startswith("/carts/"):
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return self._carts_state[0] if self._carts_state else {}

        context.status_code = 200
        context.headers["Content-Type"] = "application/json"
        return {}

    def login_matcher(self, request, context):
        """Matcher that returns 401 for invalid credentials."""
        body = _get_request_body(request)
        username = body.get("username", "")
        password = body.get("password", "")
        if username == "mor_2314" and password == "83r5^_":
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return self.login
        context.status_code = 401
        context.headers["Content-Type"] = "application/json"
        return {"error": "Invalid credentials"}

    def register_mocks(self, requests_mock):
        """Register all mock handlers with requests_mock."""
        requests_mock.get(requests_mock_module.ANY, json=self.mock_get)
        requests_mock.post(requests_mock_module.ANY, json=self.mock_post)
        requests_mock.put(requests_mock_module.ANY, json=self.mock_put)
        requests_mock.patch(requests_mock_module.ANY, json=self.mock_patch)
        requests_mock.delete(requests_mock_module.ANY, json=self.mock_delete)
        requests_mock.post(
            f"{self.base_url}/auth/login",
            json=self.login_matcher,
        )


@pytest.fixture(autouse=True)
def mock_external_api(requests_mock):
    """Mock external API calls when MOCK_API setting is enabled."""
    if MOCK_API:
        builder = APIMockBuilder(BASE_URL)
        builder.register_mocks(requests_mock)
        yield builder
    else:
        yield None


@pytest.fixture
def mock_api_builder() -> APIMockBuilder:
    """Provide an APIMockBuilder instance for custom mock configuration."""
    return APIMockBuilder(BASE_URL)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Provide the base API URL from settings."""
    return BASE_URL


@pytest.fixture
def valid_credentials() -> dict:
    """Provide valid login credentials for FakeStore API."""
    return {"username": "mor_2314", "password": "83r5^_"}


@pytest.fixture
def invalid_credentials() -> dict:
    """Provide invalid login credentials for negative testing."""
    return {"username": "invalid_user", "password": "wrong_password"}


@pytest.fixture
def test_product_ids() -> List[int]:
    """Provide a list of valid product IDs for testing."""
    return [1, 2, 3, 4, 5]


@pytest.fixture
def test_user_ids() -> List[int]:
    """Provide a list of valid user IDs for testing."""
    return [1, 2, 3]


@pytest.fixture
def test_cart_ids() -> List[int]:
    """Provide a list of valid cart IDs for testing."""
    return [1, 2, 3]


@pytest.fixture
def performance_thresholds() -> Dict[str, float]:
    """Provide performance thresholds for SLA testing."""
    return {
        "api_response_time": 2.0,  # seconds
        "login_response_time": 1.0,
        "product_list_response_time": 1.5,
        "product_detail_response_time": 1.0,
    }


@contextmanager
def temporary_mock(requests_mock, path: str, method: str, response: Any, status_code: int = 200):
    """Context manager for temporarily adding a mock response."""
    matcher = requests_mock.request(method.upper(), path, json=response, status_code=status_code)
    try:
        yield matcher
    finally:
        requests_mock.remove_matcher(matcher)


@pytest.fixture
def temp_mock(requests_mock):
    """Provide a temporary mock context manager."""
    return temporary_mock