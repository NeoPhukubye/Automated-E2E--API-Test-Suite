import pytest


@pytest.mark.api
class TestProductsPagination:
    """Tests for sort and limit query parameters on /products."""

    def test_sort_ascending(self, api):
        response = api.get("/products", params={"sort": "asc"})
        assert response.status_code == 200
        products = response.json()
        ids = [p["id"] for p in products]
        assert ids == sorted(ids)

    def test_sort_descending(self, api):
        response = api.get("/products", params={"sort": "desc"})
        assert response.status_code == 200
        products = response.json()
        ids = [p["id"] for p in products]
        assert ids == sorted(ids, reverse=True)

    def test_limit_one(self, api):
        response = api.get("/products", params={"limit": 1})
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_limit_ten(self, api):
        response = api.get("/products", params={"limit": 10})
        assert response.status_code == 200
        assert len(response.json()) == 10

    def test_sort_and_limit_combined(self, api):
        response = api.get("/products", params={"sort": "desc", "limit": 3})
        assert response.status_code == 200
        products = response.json()
        assert len(products) == 3
        ids = [p["id"] for p in products]
        assert ids == sorted(ids, reverse=True)


@pytest.mark.api
class TestCartsPagination:
    """Tests for sort and limit query parameters on /carts."""

    def test_sort_ascending(self, api):
        response = api.get("/carts", params={"sort": "asc"})
        assert response.status_code == 200
        carts = response.json()
        ids = [c["id"] for c in carts]
        assert ids == sorted(ids)

    def test_sort_descending(self, api):
        response = api.get("/carts", params={"sort": "desc"})
        assert response.status_code == 200
        carts = response.json()
        ids = [c["id"] for c in carts]
        assert ids == sorted(ids, reverse=True)

    def test_limit_two(self, api):
        response = api.get("/carts", params={"limit": 2})
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_sort_and_limit_combined(self, api):
        response = api.get("/carts", params={"sort": "asc", "limit": 2})
        assert response.status_code == 200
        carts = response.json()
        assert len(carts) == 2
        ids = [c["id"] for c in carts]
        assert ids == sorted(ids)


@pytest.mark.api
class TestUsersPagination:
    """Tests for sort and limit query parameters on /users."""

    def test_sort_ascending(self, api):
        response = api.get("/users", params={"sort": "asc"})
        assert response.status_code == 200
        users = response.json()
        ids = [u["id"] for u in users]
        assert ids == sorted(ids)

    def test_sort_descending(self, api):
        response = api.get("/users", params={"sort": "desc"})
        assert response.status_code == 200
        users = response.json()
        ids = [u["id"] for u in users]
        assert ids == sorted(ids, reverse=True)

    def test_limit_two(self, api):
        response = api.get("/users", params={"limit": 2})
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_sort_and_limit_combined(self, api):
        response = api.get("/users", params={"sort": "desc", "limit": 4})
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 4
        ids = [u["id"] for u in users]
        assert ids == sorted(ids, reverse=True)
