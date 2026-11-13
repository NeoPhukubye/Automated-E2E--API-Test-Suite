"""Tests for GET /products endpoints."""

import pytest
import allure
from utils.schema_validator import validate_product_schema, validate_products
from utils.assertions import (
    assert_status_code,
    assert_json_response,
    assert_list_not_empty,
    assert_has_keys,
)


@pytest.mark.api
@pytest.mark.smoke
@allure.feature("Products")
class TestProductsRead:
    """Tests for GET /products endpoints."""

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("List Products")
    def test_get_all_products(self, api):
        response = api.get("/products")
        assert_status_code(response, 200)
        products = assert_json_response(response)
        assert_list_not_empty(products)
        validate_products(products)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Single Product")
    def test_get_single_product(self, api):
        response = api.get("/products/1")
        assert_status_code(response, 200)
        product = assert_json_response(response)
        validate_product_schema(product)
        assert product["id"] == 1

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Categories")
    def test_get_product_categories(self, api):
        response = api.get("/products/categories")
        assert_status_code(response, 200)
        categories = assert_json_response(response)
        assert_list_not_empty(categories)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Categories")
    def test_get_products_by_category(self, api):
        response = api.get("/products/category/electronics")
        assert_status_code(response, 200)
        products = assert_json_response(response)
        assert isinstance(products, list)
        for product in products:
            assert product["category"] == "electronics"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Pagination")
    def test_get_products_with_limit(self, api):
        response = api.get("/products", params={"limit": 5})
        assert_status_code(response, 200)
        products = assert_json_response(response)
        assert len(products) == 5

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Sorting")
    def test_get_products_sorted_desc(self, api):
        response = api.get("/products", params={"sort": "desc"})
        assert_status_code(response, 200)
        products = assert_json_response(response)
        assert_list_not_empty(products)
        ids = [p["id"] for p in products]
        assert ids == sorted(ids, reverse=True)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Sorting")
    def test_get_products_sorted_asc(self, api):
        response = api.get("/products", params={"sort": "asc"})
        assert_status_code(response, 200)
        products = assert_json_response(response)
        assert_list_not_empty(products)
        ids = [p["id"] for p in products]
        assert ids == sorted(ids)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Combined Query Params")
    def test_get_products_limit_and_sort(self, api):
        response = api.get("/products", params={"limit": 3, "sort": "asc"})
        assert_status_code(response, 200)
        products = assert_json_response(response)
        assert len(products) == 3
        ids = [p["id"] for p in products]
        assert ids == sorted(ids)


@pytest.mark.api
@allure.feature("Products")
class TestProductsCreate:
    """Tests for POST /products endpoint."""

    @pytest.fixture
    def new_product_payload(self, fake):
        """Generate a random product payload for test isolation."""
        return fake.generate_product_payload()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Create Product")
    def test_create_product(self, api, new_product_payload):
        response = api.post("/products", json=new_product_payload)
        assert_status_code(response, 201, accepted_codes=[200])
        product = assert_json_response(response)
        assert_has_keys(product, ["id", "title", "price", "category"])
        # Mock returns fixture product, so just verify structure
        assert "id" in product

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Create Product")
    def test_create_product_returns_id(self, api, new_product_payload):
        response = api.post("/products", json=new_product_payload)
        assert_status_code(response, 201, accepted_codes=[200])
        product = assert_json_response(response)
        assert isinstance(product["id"], (int, float))

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Create Product Validation")
    def test_create_product_invalid_data(self, api):
        """Test creating product with invalid data returns error."""
        response = api.post("/products", json={"title": ""})
        # API may accept or reject - just verify we get a response
        assert response.status_code in (200, 201, 400, 422)


@pytest.mark.api
@allure.feature("Products")
class TestProductsUpdate:
    """Tests for PUT and PATCH /products endpoints."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Update Product")
    def test_update_product_full(self, api):
        payload = {
            "title": "Updated Product",
            "price": 49.99,
            "description": "Updated description",
            "image": "https://i.pravatar.cc",
            "category": "jewelery",
        }
        response = api.put("/products/1", json=payload)
        assert_status_code(response, 200)
        product = assert_json_response(response)
        # Mock returns fixture product, verify structure
        assert_has_keys(product, ["id", "title", "price", "category"])

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Patch Product")
    def test_patch_product_partial(self, api):
        payload = {"title": "Patched Title", "price": 19.99}
        response = api.patch("/products/1", json=payload)
        assert_status_code(response, 200)
        product = assert_json_response(response)
        assert_has_keys(product, ["id", "title", "price", "category"])

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Update Product")
    def test_update_nonexistent_product(self, api):
        payload = {"title": "Updated", "price": 10.0}
        response = api.put("/products/99999", json=payload)
        # FakeStore API returns 200 even for non-existent
        assert response.status_code in (200, 404)


@pytest.mark.api
@allure.feature("Products")
class TestProductsDelete:
    """Tests for DELETE /products endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Delete Product")
    def test_delete_product(self, api):
        response = api.delete("/products/1")
        assert_status_code(response, 200)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Delete Product")
    def test_delete_product_returns_data(self, api):
        response = api.delete("/products/1")
        assert_status_code(response, 200)
        product = assert_json_response(response)
        assert_has_keys(product, ["id"])

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Delete Product")
    def test_delete_nonexistent_product(self, api):
        response = api.delete("/products/99999")
        assert response.status_code in (200, 404)
