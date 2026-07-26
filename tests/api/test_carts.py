import pytest
from utils.schema_validator import validate_cart_schema


@pytest.mark.api
@pytest.mark.smoke
class TestCartsRead:
    """Tests for GET /carts endpoints."""

    def test_get_all_carts(self, api):
        response = api.get("/carts")
        assert response.status_code == 200
        carts = response.json()
        assert isinstance(carts, list)
        assert len(carts) > 0

    def test_get_single_cart(self, api):
        response = api.get("/carts/1")
        assert response.status_code == 200
        cart = response.json()
        validate_cart_schema(cart)
        assert cart["id"] == 1

    def test_get_carts_with_limit(self, api):
        response = api.get("/carts", params={"limit": 3})
        assert response.status_code == 200
        carts = response.json()
        assert len(carts) == 3

    def test_get_carts_sorted_desc(self, api):
        response = api.get("/carts", params={"sort": "desc"})
        assert response.status_code == 200
        carts = response.json()
        ids = [c["id"] for c in carts]
        assert ids == sorted(ids, reverse=True)

    def test_get_carts_in_date_range(self, api):
        response = api.get(
            "/carts", params={"startdate": "2020-01-01", "enddate": "2020-12-31"}
        )
        assert response.status_code == 200
        carts = response.json()
        assert isinstance(carts, list)

    def test_get_user_carts(self, api):
        response = api.get("/carts/user/1")
        assert response.status_code == 200
        carts = response.json()
        assert isinstance(carts, list)
        for cart in carts:
            assert cart["userId"] == 1


@pytest.mark.api
class TestCartsCreate:
    """Tests for POST /carts endpoint."""

    @pytest.fixture
    def new_cart_payload(self):
        return {
            "userId": 1,
            "date": "2024-01-15",
            "products": [
                {"productId": 1, "quantity": 2},
                {"productId": 3, "quantity": 1},
            ],
        }

    def test_create_cart(self, api, new_cart_payload):
        response = api.post("/carts", json=new_cart_payload)
        assert response.status_code in (200, 201)
        cart = response.json()
        assert "id" in cart

    def test_create_cart_preserves_products(self, api, new_cart_payload):
        response = api.post("/carts", json=new_cart_payload)
        assert response.status_code in (200, 201)
        cart = response.json()
        assert "products" in cart
        assert len(cart["products"]) == 2


@pytest.mark.api
class TestCartsUpdate:
    """Tests for PUT and PATCH /carts endpoints."""

    def test_update_cart_full(self, api):
        payload = {
            "userId": 2,
            "date": "2024-02-20",
            "products": [{"productId": 5, "quantity": 3}],
        }
        response = api.put("/carts/1", json=payload)
        assert response.status_code == 200
        cart = response.json()
        assert cart["userId"] == payload["userId"]

    def test_patch_cart_partial(self, api):
        payload = {"products": [{"productId": 7, "quantity": 1}]}
        response = api.patch("/carts/1", json=payload)
        assert response.status_code == 200
        cart = response.json()
        assert "products" in cart


@pytest.mark.api
class TestCartsDelete:
    """Tests for DELETE /carts endpoint."""

    def test_delete_cart(self, api):
        response = api.delete("/carts/1")
        assert response.status_code == 200

    def test_delete_cart_returns_data(self, api):
        response = api.delete("/carts/1")
        assert response.status_code == 200
        cart = response.json()
        assert "id" in cart
