import pytest


@pytest.mark.api
class TestProductsNegative:
    """Negative and edge-case tests for /products endpoints."""

    def test_get_nonexistent_product(self, api):
        response = api.get("/products/9999")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            assert response.json() in (None, "", {})

    def test_get_product_invalid_id_string(self, api):
        response = api.get("/products/abc")
        assert response.status_code in (400, 404, 500)

    def test_get_product_negative_id(self, api):
        response = api.get("/products/-1")
        assert response.status_code in (200, 400, 404)

    def test_get_product_zero_id(self, api):
        response = api.get("/products/0")
        assert response.status_code in (200, 400, 404)

    def test_create_product_empty_body(self, api):
        response = api.post("/products", json={})
        assert response.status_code in (200, 201, 400)

    def test_create_product_invalid_price(self, api):
        payload = {
            "title": "Bad Product",
            "price": "not_a_number",
            "description": "test",
            "image": "https://i.pravatar.cc",
            "category": "electronics",
        }
        response = api.post("/products", json=payload)
        assert response.status_code in (200, 201, 400, 422)

    def test_get_products_invalid_category(self, api):
        response = api.get("/products/category/nonexistent_category_xyz")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            products = response.json()
            assert isinstance(products, list)
            assert len(products) == 0

    def test_get_products_limit_zero(self, api):
        response = api.get("/products", params={"limit": 0})
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)

    def test_get_products_limit_negative(self, api):
        response = api.get("/products", params={"limit": -1})
        assert response.status_code in (200, 400)


@pytest.mark.api
class TestCartsNegative:
    """Negative and edge-case tests for /carts endpoints."""

    def test_get_nonexistent_cart(self, api):
        response = api.get("/carts/9999")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            assert response.json() in (None, "", {})

    def test_get_cart_invalid_id(self, api):
        response = api.get("/carts/abc")
        assert response.status_code in (400, 404, 500)

    def test_get_user_carts_nonexistent_user(self, api):
        response = api.get("/carts/user/9999")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            carts = response.json()
            assert isinstance(carts, list)
            assert len(carts) == 0

    def test_create_cart_empty_products(self, api):
        payload = {"userId": 1, "date": "2024-01-01", "products": []}
        response = api.post("/carts", json=payload)
        assert response.status_code in (200, 201, 400)

    def test_create_cart_missing_userid(self, api):
        payload = {"date": "2024-01-01", "products": [{"productId": 1, "quantity": 1}]}
        response = api.post("/carts", json=payload)
        assert response.status_code in (200, 201, 400)

    def test_get_carts_invalid_date_range(self, api):
        response = api.get(
            "/carts", params={"startdate": "2025-01-01", "enddate": "2020-01-01"}
        )
        assert response.status_code in (200, 400)


@pytest.mark.api
class TestUsersNegative:
    """Negative and edge-case tests for /users endpoints."""

    def test_get_nonexistent_user(self, api):
        response = api.get("/users/9999")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            assert response.json() in (None, "", {})

    def test_get_user_invalid_id(self, api):
        response = api.get("/users/abc")
        assert response.status_code in (400, 404, 500)

    def test_create_user_empty_body(self, api):
        response = api.post("/users", json={})
        assert response.status_code in (200, 201, 400)

    def test_create_user_duplicate_username(self, api):
        payload = {
            "email": "dup@test.com",
            "username": "mor_2314",
            "password": "pass123",
            "name": {"firstname": "Dup", "lastname": "User"},
            "address": {
                "city": "Test",
                "street": "1 St",
                "number": 1,
                "zipcode": "0000",
                "geolocation": {"lat": "0", "long": "0"},
            },
            "phone": "000-000-0000",
        }
        response = api.post("/users", json=payload)
        assert response.status_code in (200, 201, 400, 409)

    def test_create_user_invalid_email(self, api):
        payload = {
            "email": "not-an-email",
            "username": "baduser",
            "password": "pass",
            "name": {"firstname": "Bad", "lastname": "Email"},
            "address": {
                "city": "X",
                "street": "X",
                "number": 0,
                "zipcode": "0",
                "geolocation": {"lat": "0", "long": "0"},
            },
            "phone": "000",
        }
        response = api.post("/users", json=payload)
        assert response.status_code in (200, 201, 400, 422)
