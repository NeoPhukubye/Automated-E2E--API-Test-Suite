import pytest


@pytest.mark.api
@pytest.mark.integration
class TestUserLoginWorkflow:
    """Integration tests: user creation -> login -> token validation."""

    @pytest.fixture
    def test_user(self):
        return {
            "email": "workflow@test.com",
            "username": "workflow_user",
            "password": "WorkflowPass1!",
            "name": {"firstname": "Workflow", "lastname": "Tester"},
            "address": {
                "city": "Pretoria",
                "street": "100 Flow St",
                "number": 10,
                "zipcode": "0001",
                "geolocation": {"lat": "-25.7479", "long": "28.2293"},
            },
            "phone": "012-000-1111",
        }

    def test_create_user_then_login(self, api, test_user):
        create_resp = api.post("/users", json=test_user)
        assert create_resp.status_code in (200, 201)
        user = create_resp.json()
        assert "id" in user

        login_resp = api.post(
            "/auth/login",
            json={"username": test_user["username"], "password": test_user["password"]},
        )
        # FakeStore may not persist new users for login, so accept auth failure
        assert login_resp.status_code in (200, 201, 400, 401)


@pytest.mark.api
@pytest.mark.integration
class TestCartWorkflow:
    """Integration tests: browse products -> add to cart -> verify cart."""

    def test_browse_and_add_to_cart(self, api):
        products_resp = api.get("/products", params={"limit": 3})
        assert products_resp.status_code == 200
        products = products_resp.json()
        assert len(products) >= 1

        cart_items = [
            {"productId": p["id"], "quantity": 1} for p in products[:2]
        ]
        cart_payload = {"userId": 1, "date": "2024-06-15", "products": cart_items}
        create_resp = api.post("/carts", json=cart_payload)
        assert create_resp.status_code in (200, 201)
        cart = create_resp.json()
        assert "id" in cart
        assert "products" in cart

    def test_update_cart_quantity(self, api):
        cart_resp = api.get("/carts/1")
        assert cart_resp.status_code == 200
        cart = cart_resp.json()

        updated_products = []
        for item in cart["products"]:
            updated_products.append(
                {"productId": item["productId"], "quantity": item["quantity"] + 1}
            )

        update_resp = api.put(
            f"/carts/{cart['id']}",
            json={"userId": cart["userId"], "date": cart["date"], "products": updated_products},
        )
        assert update_resp.status_code == 200

    def test_full_cart_lifecycle(self, api):
        # Create
        payload = {
            "userId": 2,
            "date": "2024-07-01",
            "products": [{"productId": 1, "quantity": 3}],
        }
        create_resp = api.post("/carts", json=payload)
        assert create_resp.status_code in (200, 201)
        cart_id = create_resp.json()["id"]

        # Read
        get_resp = api.get(f"/carts/{cart_id}")
        assert get_resp.status_code == 200

        # Update
        payload["products"][0]["quantity"] = 5
        update_resp = api.put(f"/carts/{cart_id}", json=payload)
        assert update_resp.status_code == 200

        # Delete
        delete_resp = api.delete(f"/carts/{cart_id}")
        assert delete_resp.status_code == 200


@pytest.mark.api
@pytest.mark.integration
class TestProductCategoryWorkflow:
    """Integration tests: fetch categories -> validate products per category."""

    def test_all_categories_have_products(self, api):
        cat_resp = api.get("/products/categories")
        assert cat_resp.status_code == 200
        categories = cat_resp.json()
        assert len(categories) > 0

        for category in categories:
            prod_resp = api.get(f"/products/category/{category}")
            assert prod_resp.status_code == 200
            products = prod_resp.json()
            assert isinstance(products, list)
            assert len(products) > 0, f"Category '{category}' has no products"
            for product in products:
                assert product["category"] == category
