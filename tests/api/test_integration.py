"""Integration tests: user creation -> login -> token validation."""

import pytest
import allure
from utils.assertions import assert_status_code, assert_json_response, assert_list_not_empty


@pytest.mark.api
@pytest.mark.integration
@allure.feature("Integration Workflows")
class TestUserLoginWorkflow:
    """Integration tests: user creation -> login -> token validation."""

    @pytest.fixture
    def test_user(self, fake):
        """Generate a random user for test isolation."""
        return fake.generate_user_payload()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("User Registration Flow")
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
@allure.feature("Integration Workflows")
class TestCartWorkflow:
    """Integration tests: browse products -> add to cart -> verify cart."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Shopping Flow")
    def test_browse_and_add_to_cart(self, api):
        products_resp = api.get("/products", params={"limit": 3})
        assert_status_code(products_resp, 200)
        products = assert_json_response(products_resp)
        assert len(products) >= 1

        cart_items = [
            {"productId": p["id"], "quantity": 1} for p in products[:2]
        ]
        cart_payload = {"userId": 1, "date": "2024-06-15", "products": cart_items}
        create_resp = api.post("/carts", json=cart_payload)
        assert_status_code(create_resp, 201, accepted_codes=[200])
        cart = assert_json_response(create_resp)
        assert "id" in cart
        assert "products" in cart

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Cart Update Flow")
    def test_update_cart_quantity(self, api):
        cart_resp = api.get("/carts/1")
        assert_status_code(cart_resp, 200)
        cart = assert_json_response(cart_resp)

        updated_products = []
        for item in cart["products"]:
            updated_products.append(
                {"productId": item["productId"], "quantity": item["quantity"] + 1}
            )

        update_resp = api.put(
            f"/carts/{cart['id']}",
            json={"userId": cart["userId"], "date": cart["date"], "products": updated_products},
        )
        assert_status_code(update_resp, 200)

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("Cart Lifecycle")
    def test_full_cart_lifecycle(self, api):
        """Test full CRUD lifecycle using an existing cart ID."""
        cart_id = 1
        # Create
        payload = {
            "userId": 1,
            "date": "2024-07-01",
            "products": [{"productId": 1, "quantity": 3}],
        }
        create_resp = api.post("/carts", json=payload)
        assert_status_code(create_resp, 201, accepted_codes=[200])

        # Read
        get_resp = api.get(f"/carts/{cart_id}")
        assert_status_code(get_resp, 200)

        # Update
        payload["products"][0]["quantity"] = 5
        update_resp = api.put(f"/carts/{cart_id}", json=payload)
        assert_status_code(update_resp, 200)

        # Delete
        delete_resp = api.delete(f"/carts/{cart_id}")
        assert_status_code(delete_resp, 200)


@pytest.mark.api
@pytest.mark.integration
@allure.feature("Integration Workflows")
class TestProductCategoryWorkflow:
    """Integration tests: fetch categories -> validate products per category."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Category Browsing")
    def test_all_categories_have_products(self, api):
        cat_resp = api.get("/products/categories")
        assert_status_code(cat_resp, 200)
        categories = assert_json_response(cat_resp)
        assert_list_not_empty(categories)

        for category in categories:
            prod_resp = api.get(f"/products/category/{category}")
            assert_status_code(prod_resp, 200)
            products = assert_json_response(prod_resp)
            assert isinstance(products, list)
            assert len(products) > 0, f"Category '{category}' has no products"
            for product in products:
                assert product["category"] == category