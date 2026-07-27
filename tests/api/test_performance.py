import pytest
import allure
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


@pytest.mark.api
@allure.feature("Performance")
class TestResponseTimeSLA:
    """Validate API response times against SLA thresholds."""

    SLA_FAST = 2.0  # seconds - single resource
    SLA_NORMAL = 5.0  # seconds - list endpoints
    SLA_WRITE = 5.0  # seconds - create/update/delete

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("GET Endpoints")
    def test_get_single_product_sla(self, api):
        """Single product should respond within fast SLA."""
        response = api.get("/products/1")
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < self.SLA_FAST

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("GET Endpoints")
    def test_get_all_products_sla(self, api):
        """Product listing should respond within normal SLA."""
        response = api.get("/products")
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < self.SLA_NORMAL

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("GET Endpoints")
    def test_get_single_user_sla(self, api):
        """Single user should respond within fast SLA."""
        response = api.get("/users/1")
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < self.SLA_FAST

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("GET Endpoints")
    def test_get_all_users_sla(self, api):
        """User listing should respond within normal SLA."""
        response = api.get("/users")
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < self.SLA_NORMAL

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("GET Endpoints")
    def test_get_all_carts_sla(self, api):
        """Cart listing should respond within normal SLA."""
        response = api.get("/carts")
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < self.SLA_NORMAL

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("POST Endpoints")
    def test_create_product_sla(self, api):
        """Creating a product should respond within write SLA."""
        payload = {
            "title": "SLA Test Product",
            "price": 10.00,
            "description": "performance test",
            "image": "https://i.pravatar.cc",
            "category": "electronics",
        }
        response = api.post("/products", json=payload)
        assert response.status_code in (200, 201)
        assert response.elapsed.total_seconds() < self.SLA_WRITE

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Auth Endpoints")
    def test_login_sla(self, api):
        """Login should respond within write SLA."""
        response = api.post(
            "/auth/login", json={"username": "mor_2314", "password": "83r5^_"}
        )
        assert response.status_code in (200, 201)
        assert response.elapsed.total_seconds() < self.SLA_WRITE


@pytest.mark.api
@allure.feature("Performance")
class TestConcurrentLoad:
    """Validate API stability under concurrent request load."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Concurrent Reads")
    def test_concurrent_product_reads(self, api):
        """API should handle 10 concurrent product reads without errors."""
        results = self._run_concurrent(api, "/products/1", count=10)
        assert all(r == 200 for r in results), f"Failed responses: {results}"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Concurrent Reads")
    def test_concurrent_user_reads(self, api):
        """API should handle 10 concurrent user reads without errors."""
        results = self._run_concurrent(api, "/users/1", count=10)
        assert all(r == 200 for r in results), f"Failed responses: {results}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Concurrent Reads")
    def test_concurrent_mixed_reads(self, api):
        """API should handle concurrent reads across different endpoints."""
        endpoints = ["/products", "/users", "/carts", "/products/1", "/users/1"]
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(api.get, endpoint): endpoint
                for endpoint in endpoints
            }
            for future in as_completed(futures):
                response = future.result()
                results.append(response.status_code)
        assert all(r == 200 for r in results), f"Failed responses: {results}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Sustained Load")
    def test_sequential_rapid_requests(self, api):
        """API should handle 20 rapid sequential requests without degradation."""
        times = []
        for _ in range(20):
            response = api.get("/products/1")
            assert response.status_code == 200
            times.append(response.elapsed.total_seconds())
        avg_time = sum(times) / len(times)
        max_time = max(times)
        assert avg_time < 3.0, f"Average response time {avg_time:.2f}s exceeds threshold"
        assert max_time < 10.0, f"Max response time {max_time:.2f}s exceeds threshold"

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Sustained Load")
    def test_response_time_consistency(self, api):
        """Response times should not vary wildly (std dev check)."""
        times = []
        for _ in range(10):
            response = api.get("/products")
            assert response.status_code == 200
            times.append(response.elapsed.total_seconds())
        avg = sum(times) / len(times)
        variance = sum((t - avg) ** 2 for t in times) / len(times)
        std_dev = variance ** 0.5
        assert std_dev < avg * 2, f"High variance: std_dev={std_dev:.2f}, avg={avg:.2f}"

    def _run_concurrent(self, api, endpoint: str, count: int) -> list[int]:
        """Run concurrent GET requests and return status codes."""
        with ThreadPoolExecutor(max_workers=count) as executor:
            futures = [executor.submit(api.get, endpoint) for _ in range(count)]
            return [f.result().status_code for f in as_completed(futures)]
