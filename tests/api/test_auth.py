import pytest


@pytest.mark.api
@pytest.mark.smoke
class TestAuthLogin:
    """Tests for POST /auth/login endpoint."""

    @pytest.fixture
    def valid_credentials(self):
        return {"username": "mor_2314", "password": "83r5^_"}

    def test_login_success(self, api, valid_credentials):
        response = api.post("/auth/login", json=valid_credentials)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0

    def test_login_invalid_password(self, api):
        response = api.post(
            "/auth/login", json={"username": "mor_2314", "password": "wrongpass"}
        )
        assert response.status_code in (400, 401)

    def test_login_invalid_username(self, api):
        response = api.post(
            "/auth/login", json={"username": "nonexistent_user", "password": "83r5^_"}
        )
        assert response.status_code in (400, 401)

    def test_login_empty_credentials(self, api):
        response = api.post("/auth/login", json={"username": "", "password": ""})
        assert response.status_code in (400, 401)

    def test_login_missing_fields(self, api):
        response = api.post("/auth/login", json={})
        assert response.status_code in (400, 401)
