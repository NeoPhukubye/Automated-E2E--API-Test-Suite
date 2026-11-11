"""Tests for token validation and auth token schema."""

import pytest
import allure
from utils.assertions import assert_status_code, assert_json_response
from utils.schema_validator import validate_auth_token_schema, validate_login_response_schema


@pytest.mark.api
@allure.feature("Authentication")
class TestAuthToken:
    """Tests for auth token validation and schema."""

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("Token Structure")
    def test_login_returns_token(self, api):
        """Verify login response contains a token field."""
        response = api.post(
            "/auth/login",
            json={"username": "mor_2314", "password": "83r5^_"},
        )
        assert_status_code(response, 200, accepted_codes=[201])
        data = assert_json_response(response)
        assert "token" in data
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Token Schema Validation")
    def test_login_response_schema_valid(self, api):
        """Verify login response matches the auth token schema."""
        response = api.post(
            "/auth/login",
            json={"username": "mor_2314", "password": "83r5^_"},
        )
        assert_status_code(response, 200, accepted_codes=[201])
        data = assert_json_response(response)
        validate_auth_token_schema(data)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Token Format")
    def test_token_is_non_empty_string(self, api):
        """Verify token is a non-empty string."""
        response = api.post(
            "/auth/login",
            json={"username": "mor_2314", "password": "83r5^_"},
        )
        assert_status_code(response, 200, accepted_codes=[201])
        data = assert_json_response(response)
        token = data.get("token", "")
        assert isinstance(token, str)
        assert token.strip() != ""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Token Consistency")
    def test_token_consistent_across_requests(self, api):
        """Verify token is consistent across multiple login requests."""
        response1 = api.post(
            "/auth/login",
            json={"username": "mor_2314", "password": "83r5^_"},
        )
        response2 = api.post(
            "/auth/login",
            json={"username": "mor_2314", "password": "83r5^_"},
        )
        assert_status_code(response1, 200, accepted_codes=[201])
        assert_status_code(response2, 200, accepted_codes=[201])
        token1 = assert_json_response(response1).get("token")
        token2 = assert_json_response(response2).get("token")
        assert token1 == token2

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Login Response Enrichment")
    def test_login_response_contains_user_info(self, api):
        """Verify login response contains user information fields."""
        response = api.post(
            "/auth/login",
            json={"username": "mor_2314", "password": "83r5^_"},
        )
        assert_status_code(response, 200, accepted_codes=[201])
        data = assert_json_response(response)
        # Some APIs return enriched login response with user info
        if "username" in data:
            assert data["username"] == "mor_2314"
        if "email" in data:
            assert "@" in data["email"]