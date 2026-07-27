import pytest
import allure


@pytest.mark.api
@allure.feature("Data Consistency")
class TestProductDataConsistency:
    """Validate data integrity and consistency of product responses."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Unique IDs")
    def test_all_products_have_unique_ids(self, api):
        response = api.get("/products")
        products = response.json()
        ids = [p["id"] for p in products]
        assert len(ids) == len(set(ids)), "Duplicate product IDs found"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Data Validation")
    def test_all_products_have_positive_prices(self, api):
        response = api.get("/products")
        products = response.json()
        for product in products:
            assert product["price"] > 0, f"Product {product['id']} has non-positive price"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Data Validation")
    def test_all_products_have_non_empty_titles(self, api):
        response = api.get("/products")
        products = response.json()
        for product in products:
            assert product["title"].strip(), f"Product {product['id']} has empty title"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Referential Integrity")
    def test_all_products_have_valid_categories(self, api):
        cat_resp = api.get("/products/categories")
        valid_categories = cat_resp.json()

        prod_resp = api.get("/products")
        products = prod_resp.json()
        for product in products:
            assert product["category"] in valid_categories, (
                f"Product {product['id']} has invalid category: {product['category']}"
            )

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Data Validation")
    def test_all_products_have_image_urls(self, api):
        response = api.get("/products")
        products = response.json()
        for product in products:
            assert product["image"].startswith("http"), (
                f"Product {product['id']} has invalid image URL"
            )

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Referential Integrity")
    def test_product_count_matches_category_totals(self, api):
        all_resp = api.get("/products")
        all_products = all_resp.json()

        cat_resp = api.get("/products/categories")
        categories = cat_resp.json()

        category_total = 0
        for category in categories:
            resp = api.get(f"/products/category/{category}")
            category_total += len(resp.json())

        assert category_total == len(all_products)


@pytest.mark.api
@allure.feature("Data Consistency")
class TestCartDataConsistency:
    """Validate data integrity and consistency of cart responses."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Unique IDs")
    def test_all_carts_have_unique_ids(self, api):
        response = api.get("/carts")
        carts = response.json()
        ids = [c["id"] for c in carts]
        assert len(ids) == len(set(ids)), "Duplicate cart IDs found"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Data Validation")
    def test_all_carts_have_valid_user_ids(self, api):
        response = api.get("/carts")
        carts = response.json()
        for cart in carts:
            assert cart["userId"] > 0, f"Cart {cart['id']} has invalid userId"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Data Validation")
    def test_all_carts_have_products(self, api):
        response = api.get("/carts")
        carts = response.json()
        for cart in carts:
            assert len(cart["products"]) > 0, f"Cart {cart['id']} has no products"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Data Validation")
    def test_cart_products_have_positive_quantities(self, api):
        response = api.get("/carts")
        carts = response.json()
        for cart in carts:
            for item in cart["products"]:
                assert item["quantity"] > 0, (
                    f"Cart {cart['id']} has item with non-positive quantity"
                )

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Referential Integrity")
    def test_cart_product_ids_are_valid(self, api):
        prod_resp = api.get("/products")
        valid_ids = {p["id"] for p in prod_resp.json()}

        cart_resp = api.get("/carts")
        carts = cart_resp.json()
        for cart in carts:
            for item in cart["products"]:
                assert item["productId"] in valid_ids, (
                    f"Cart {cart['id']} references invalid productId {item['productId']}"
                )


@pytest.mark.api
@allure.feature("Data Consistency")
class TestUserDataConsistency:
    """Validate data integrity and consistency of user responses."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Unique IDs")
    def test_all_users_have_unique_ids(self, api):
        response = api.get("/users")
        users = response.json()
        ids = [u["id"] for u in users]
        assert len(ids) == len(set(ids)), "Duplicate user IDs found"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Unique Data")
    def test_all_users_have_unique_usernames(self, api):
        response = api.get("/users")
        users = response.json()
        usernames = [u["username"] for u in users]
        assert len(usernames) == len(set(usernames)), "Duplicate usernames found"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Data Validation")
    def test_all_users_have_email_format(self, api):
        response = api.get("/users")
        users = response.json()
        for user in users:
            assert "@" in user["email"], f"User {user['id']} has invalid email"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Data Validation")
    def test_all_users_have_complete_names(self, api):
        response = api.get("/users")
        users = response.json()
        for user in users:
            assert user["name"]["firstname"].strip(), f"User {user['id']} missing firstname"
            assert user["name"]["lastname"].strip(), f"User {user['id']} missing lastname"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Data Validation")
    def test_all_users_have_addresses(self, api):
        response = api.get("/users")
        users = response.json()
        for user in users:
            addr = user["address"]
            assert "city" in addr
            assert "street" in addr
            assert "zipcode" in addr
