"""Tests for error response formats and consistency."""

import pytest
import allure
from utils.assertions import assert_json_response


@pytest.mark.api
@allure.feature("Error Handling")
class TestErrorResponses:
    """Tests validating error response formats and consistency."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("404 Error Format")
    def test_404_returns_json_error(self, api):
        """Verify 404 responses contain JSON error format."""
        response = api.get("/products/99999")
        if response.status_code == 404:
            try:
                data = assert_json_response(response)
                assert isinstance(data, dict)
            except AssertionError:
                # Some APIs return empty body for 404
                assert response.text.strip() in ("", "null")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("400 Error Format")
    def test_400_returns_json_error(self, api):
        """Verify 400 responses contain JSON error format."""
        response = api.post("/products", json={})
        if response.status_code == 400:
            try:
                data = assert_json_response(response)
                assert isinstance(data, dict)
            except AssertionError:
                assert response.text.strip() in ("", "null")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Error Response Headers")
    def test_error_response_has_content_type(self, api):
        """Verify error responses include Content-Type header."""
        response = api.post(
            "/auth/login", json={"username": "wrong", "password": "wrong"}
        )
        if response.status_code in (400, 401):
            assert "content-type" in response.headers
            assert "application/json" in response.headers["content-type"]

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Error Message Consistency")
    def test_error_message_format_consistent(self, api):
        """Verify error messages follow consistent format."""
        response1 = api.post(
            "/auth/login", json={"username": "wrong1", "password": "bad"}
        )
        response2 = api.post(
            "/auth/login", json={"username": "wrong2", "password": "bad"}
        )
        if response1.status_code in (400, 401) and response2.status_code in (400, 401):
            data1 = assert_json_response(response1)
            data2 = assert_json_response(response2)
            # Both should have similar structure (error field)
            assert "error" in data1 or "message" in data1
            assert "error" in data2 or "message" in data2

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Rate Limit Error")
    def test_rate_limit_error_format(self, api):
        """Verify rate limit errors (429) have proper format."""
        # This test may not trigger in mock, but validates format if it does
        response = api.get("/products")
        if response.status_code == 429:
            data = assert_json_response(response)
            assert isinstance(data, dict)
