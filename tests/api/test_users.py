import pytest
import allure
from utils.schema_validator import validate_user_schema


@pytest.mark.api
@pytest.mark.smoke
@allure.feature("Users")
class TestUsersRead:
    """Tests for GET /users endpoints."""

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("List Users")
    def test_get_all_users(self, api):
        response = api.get("/users")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Single User")
    def test_get_single_user(self, api):
        response = api.get("/users/1")
        assert response.status_code == 200
        user = response.json()
        validate_user_schema(user)
        assert user["id"] == 1

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Pagination")
    def test_get_users_with_limit(self, api):
        response = api.get("/users", params={"limit": 3})
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 3

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Sorting")
    def test_get_users_sorted_desc(self, api):
        response = api.get("/users", params={"sort": "desc"})
        assert response.status_code == 200
        users = response.json()
        ids = [u["id"] for u in users]
        assert ids == sorted(ids, reverse=True)


@pytest.mark.api
@allure.feature("Users")
class TestUsersCreate:
    """Tests for POST /users endpoint."""

    @pytest.fixture
    def new_user_payload(self):
        return {
            "email": "testuser@example.com",
            "username": "testuser_auto",
            "password": "SecurePass123",
            "name": {"firstname": "Test", "lastname": "User"},
            "address": {
                "city": "Johannesburg",
                "street": "123 Main St",
                "number": 42,
                "zipcode": "2000",
                "geolocation": {"lat": "-26.2041", "long": "28.0473"},
            },
            "phone": "012-345-6789",
        }

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Create User")
    def test_create_user(self, api, new_user_payload):
        response = api.post("/users", json=new_user_payload)
        assert response.status_code in (200, 201)
        user = response.json()
        assert "id" in user

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Create User")
    def test_create_user_returns_id(self, api, new_user_payload):
        response = api.post("/users", json=new_user_payload)
        assert response.status_code in (200, 201)
        user = response.json()
        assert isinstance(user["id"], (int, float))


@pytest.mark.api
@allure.feature("Users")
class TestUsersUpdate:
    """Tests for PUT and PATCH /users endpoints."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Update User")
    def test_update_user_full(self, api):
        payload = {
            "email": "updated@example.com",
            "username": "updated_user",
            "password": "NewPass456",
            "name": {"firstname": "Updated", "lastname": "Person"},
            "address": {
                "city": "Cape Town",
                "street": "456 Oak Ave",
                "number": 7,
                "zipcode": "8000",
                "geolocation": {"lat": "-33.9249", "long": "18.4241"},
            },
            "phone": "098-765-4321",
        }
        response = api.put("/users/1", json=payload)
        assert response.status_code == 200
        user = response.json()
        assert user["email"] == payload["email"]
        assert user["username"] == payload["username"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Patch User")
    def test_patch_user_partial(self, api):
        payload = {"email": "patched@example.com", "phone": "111-222-3333"}
        response = api.patch("/users/1", json=payload)
        assert response.status_code == 200
        user = response.json()
        assert user["email"] == payload["email"]
        assert user["phone"] == payload["phone"]


@pytest.mark.api
@allure.feature("Users")
class TestUsersDelete:
    """Tests for DELETE /users endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Delete User")
    def test_delete_user(self, api):
        response = api.delete("/users/1")
        assert response.status_code == 200

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Delete User")
    def test_delete_user_returns_data(self, api):
        response = api.delete("/users/1")
        assert response.status_code == 200
        user = response.json()
        assert "id" in user
