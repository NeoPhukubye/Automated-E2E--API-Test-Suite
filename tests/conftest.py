"""Root pytest fixtures shared across API and E2E tests."""

import os
import json
from typing import Generator
from urllib.parse import urlparse, parse_qs

import pytest
import allure
import requests_mock as requests_mock_module
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


def _get_request_body(request_proxy):
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


@pytest.fixture(autouse=True)
def mock_external_api(requests_mock):
    """Mock external API calls in CI environments or when MOCK_API is set."""
    # Allow enabling mock locally via MOCK_API=true
    should_mock = (
        os.getenv("GITHUB_ACTIONS", "").lower() in ("true",)
        or os.getenv("CI", "").lower() in ("true",)
        or os.getenv("MOCK_API", "").lower() in ("true", "1", "yes")
    )
    if should_mock:
        base = os.getenv("BASE_URL", "https://fakestoreapi.com")
        products = _load_fixture("products")
        users = _load_fixture("users")
        carts = _load_fixture("carts")
        product1 = products[0] if products else _load_fixture("product_1")
        login = _load_fixture("login")
        categories = _load_fixture("categories")

        # Use a mutable list for carts to track created/updated ones
        carts_state = list(carts)

        def _mock_get(request, context):
            # request is a _RequestObjectProxy, extract the URL string
            url_str = request.url if hasattr(request, 'url') else str(request)
            parsed = urlparse(url_str)
            query = parse_qs(parsed.query)
            path = parsed.path

            def _get_query(name, default=None):
                val = query.get(name, [default])
                return val[0] if val else default

            if path == "/products":
                limit = int(_get_query("limit", len(products)))
                sort = _get_query("sort", "")
                result = list(products)
                if sort == "desc":
                    result = sorted(result, key=lambda p: p["id"], reverse=True)
                elif sort == "asc":
                    result = sorted(result, key=lambda p: p["id"])
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return result[:limit]
            elif path.startswith("/products/category/"):
                category = path.split("/")[-1]
                # URL decode category (e.g., men%27s -> men's)
                from urllib.parse import unquote
                category = unquote(category)
                filtered = [p for p in products if p.get("category") == category]
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return filtered if filtered else []
            elif path == "/products/categories":
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return categories
            elif path.startswith("/products/"):
                pid = path.split("/")[-1]
                # Return 404 for non-numeric IDs
                if not pid.isdigit():
                    context.status_code = 404
                    context.headers["Content-Type"] = "application/json"
                    return {"error": "Product not found"}
                product = next((p for p in products if str(p.get("id")) == pid), None)
                if product is None:
                    context.status_code = 404
                    context.headers["Content-Type"] = "application/json"
                    return {"error": "Product not found"}
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return product
            elif path == "/users":
                limit = int(_get_query("limit", len(users)))
                sort = _get_query("sort", "")
                result = list(users)
                if sort == "desc":
                    result = sorted(result, key=lambda u: u["id"], reverse=True)
                elif sort == "asc":
                    result = sorted(result, key=lambda u: u["id"])
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return result[:limit]
            elif path.startswith("/users/"):
                uid = path.split("/")[-1]
                # Return 404 for non-numeric IDs
                if not uid.isdigit():
                    context.status_code = 404
                    context.headers["Content-Type"] = "application/json"
                    return {"error": "User not found"}
                user = next((u for u in users if str(u.get("id")) == uid), None)
                if user is None:
                    context.status_code = 404
                    context.headers["Content-Type"] = "application/json"
                    return {"error": "User not found"}
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return user
            elif path == "/carts":
                limit = int(_get_query("limit", len(carts)))
                sort = _get_query("sort", "")
                startdate = _get_query("startdate", "")
                enddate = _get_query("enddate", "")
                result = list(carts)
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
                return [c for c in carts if str(c.get("userId")) == uid]
            elif path.startswith("/carts/"):
                cid = path.split("/")[-1]
                # Return 404 for non-numeric IDs
                if not cid.isdigit():
                    context.status_code = 404
                    context.headers["Content-Type"] = "application/json"
                    return {"error": "Cart not found"}
                cart = next((c for c in carts if str(c.get("id")) == cid), None)
                if cart is None:
                    context.status_code = 404
                    context.headers["Content-Type"] = "application/json"
                    return {"error": "Cart not found"}
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return cart

        def _mock_post(request, context):
            url_str = request.url if hasattr(request, 'url') else str(request)
            parsed = urlparse(url_str)
            path = parsed.path
            body = _get_request_body(request)
            if path == "/auth/login":
                return login
            elif path == "/products":
                context.status_code = 201
                context.headers["Content-Type"] = "application/json"
                return {"id": 21, **body}
            elif path == "/users":
                context.status_code = 201
                context.headers["Content-Type"] = "application/json"
                return {"id": 11, **body} if users else {}
            elif path == "/carts":
                context.status_code = 201
                context.headers["Content-Type"] = "application/json"
                new_id = max([c["id"] for c in carts], default=0) + 1
                return {"id": new_id, **body}
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return {}

        def _mock_put(request, context):
            url_str = request.url if hasattr(request, 'url') else str(request)
            parsed = urlparse(url_str)
            path = parsed.path
            body = _get_request_body(request)
            if path.startswith("/products/"):
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return {**product1, **body}
            elif path.startswith("/users/"):
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return {**users[0], **body} if users else {}
            elif path.startswith("/carts/"):
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return {**carts[0], **body} if carts else {}
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return {}

        def _mock_patch(request, context):
            url_str = request.url if hasattr(request, 'url') else str(request)
            parsed = urlparse(url_str)
            path = parsed.path
            body = _get_request_body(request)
            if path.startswith("/products/"):
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return {**product1, **body}
            elif path.startswith("/users/"):
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return {**users[0], **body} if users else {}
            elif path.startswith("/carts/"):
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return {**carts[0], **body} if carts else {}
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return {}

        def _mock_delete(request, context):
            url_str = request.url if hasattr(request, 'url') else str(request)
            parsed = urlparse(url_str)
            path = parsed.path
            if path.startswith("/products/"):
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return product1
            elif path.startswith("/users/"):
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return users[0] if users else {}
            elif path.startswith("/carts/"):
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return carts[0] if carts else {}
            context.status_code = 200
            context.headers["Content-Type"] = "application/json"
            return {}

        def _login_matcher(request, context):
            """Matcher that returns 401 for invalid credentials."""
            body = _get_request_body(request)
            username = body.get("username", "")
            password = body.get("password", "")
            if username == "mor_2314" and password == "83r5^_":
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return login
            context.status_code = 401
            context.headers["Content-Type"] = "application/json"
            return {"error": "Invalid credentials"}

        # Use the imported requests_mock module for ANY constant
        # Register specific matchers AFTER ANY so they take precedence
        requests_mock.get(requests_mock_module.ANY, json=_mock_get)
        requests_mock.post(requests_mock_module.ANY, json=_mock_post)
        requests_mock.put(requests_mock_module.ANY, json=_mock_put)
        requests_mock.patch(requests_mock_module.ANY, json=_mock_patch)
        requests_mock.delete(requests_mock_module.ANY, json=_mock_delete)
        # Register login endpoint with credential-based matcher LAST for precedence
        requests_mock.post(
            f"{base}/auth/login",
            json=_login_matcher,
        )

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