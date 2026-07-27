import pytest
import allure


@pytest.mark.api
@allure.feature("Response Metadata")
class TestResponseMetadata:
    """Tests validating response headers, content-type, and response times."""

    TIMEOUT_THRESHOLD = 10  # seconds

    @pytest.mark.smoke
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Content-Type Headers")
    def test_products_response_headers(self, api):
        response = api.get("/products")
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Content-Type Headers")
    def test_carts_response_headers(self, api):
        response = api.get("/carts")
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Content-Type Headers")
    def test_users_response_headers(self, api):
        response = api.get("/users")
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Response Time")
    def test_products_response_time(self, api):
        response = api.get("/products")
        assert response.elapsed.total_seconds() < self.TIMEOUT_THRESHOLD

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Response Time")
    def test_single_product_response_time(self, api):
        response = api.get("/products/1")
        assert response.elapsed.total_seconds() < self.TIMEOUT_THRESHOLD

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Response Time")
    def test_carts_response_time(self, api):
        response = api.get("/carts")
        assert response.elapsed.total_seconds() < self.TIMEOUT_THRESHOLD

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Response Time")
    def test_users_response_time(self, api):
        response = api.get("/users")
        assert response.elapsed.total_seconds() < self.TIMEOUT_THRESHOLD

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Response Time")
    def test_auth_response_time(self, api):
        response = api.post(
            "/auth/login", json={"username": "mor_2314", "password": "83r5^_"}
        )
        assert response.elapsed.total_seconds() < self.TIMEOUT_THRESHOLD

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Content-Type Headers")
    def test_post_product_response_headers(self, api):
        payload = {
            "title": "Header Test",
            "price": 9.99,
            "description": "testing headers",
            "image": "https://i.pravatar.cc",
            "category": "electronics",
        }
        response = api.post("/products", json=payload)
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]
