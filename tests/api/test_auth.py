import pytest
import allure


@pytest.mark.api
@pytest.mark.smoke
@allure.feature("Authentication")
class TestAuthLogin:
    """Tests for POST /auth/login endpoint."""

    @pytest.fixture
    def valid_credentials(self):
        return {"username": "mor_2314", "password": "83r5^_"}

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("Valid Login")
    def test_login_success(self, api, valid_credentials):
        response = api.post("/auth/login", json=valid_credentials)
        assert response.status_code in (200, 201)
        data = response.json()
        assert "token" in data
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Invalid Credentials")
    def test_login_invalid_password(self, api):
        response = api.post(
            "/auth/login", json={"username": "mor_2314", "password": "wrongpass"}
        )
        assert response.status_code in (400, 401)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Invalid Credentials")
    def test_login_invalid_username(self, api):
        response = api.post(
            "/auth/login", json={"username": "nonexistent_user", "password": "83r5^_"}
        )
        assert response.status_code in (400, 401)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Form Validation")
    def test_login_empty_credentials(self, api):
        response = api.post("/auth/login", json={"username": "", "password": ""})
        assert response.status_code in (400, 401)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Form Validation")
    def test_login_missing_fields(self, api):
        response = api.post("/auth/login", json={})
        assert response.status_code in (400, 401)
