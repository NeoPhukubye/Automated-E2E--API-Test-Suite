import pytest
import allure
from utils.schema_validator import validate_product_schema


@pytest.mark.api
@pytest.mark.smoke
@allure.feature("Products")
class TestProductsRead:
    """Tests for GET /products endpoints."""

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("List Products")
    def test_get_all_products(self, api):
        response = api.get("/products")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) > 0

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Single Product")
    def test_get_single_product(self, api):
        response = api.get("/products/1")
        assert response.status_code == 200
        product = response.json()
        validate_product_schema(product)
        assert product["id"] == 1

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Categories")
    def test_get_product_categories(self, api):
        response = api.get("/products/categories")
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) > 0

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Categories")
    def test_get_products_by_category(self, api):
        response = api.get("/products/category/electronics")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        for product in products:
            assert product["category"] == "electronics"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Pagination")
    def test_get_products_with_limit(self, api):
        response = api.get("/products", params={"limit": 5})
        assert response.status_code == 200
        products = response.json()
        assert len(products) == 5


@pytest.mark.api
@allure.feature("Products")
class TestProductsCreate:
    """Tests for POST /products endpoint."""

    @pytest.fixture
    def new_product_payload(self):
        return {
            "title": "Test Product",
            "price": 29.99,
            "description": "A test product for automation",
            "image": "https://i.pravatar.cc",
            "category": "electronics",
        }

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Create Product")
    def test_create_product(self, api, new_product_payload):
        response = api.post("/products", json=new_product_payload)
        assert response.status_code in (200, 201)
        product = response.json()
        assert "id" in product
        assert product["title"] == new_product_payload["title"]
        assert product["price"] == new_product_payload["price"]
        assert product["category"] == new_product_payload["category"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Create Product")
    def test_create_product_returns_id(self, api, new_product_payload):
        response = api.post("/products", json=new_product_payload)
        assert response.status_code in (200, 201)
        product = response.json()
        assert isinstance(product["id"], (int, float))


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
        assert response.status_code == 200
        product = response.json()
        assert product["title"] == payload["title"]
        assert product["price"] == payload["price"]
        assert product["category"] == payload["category"]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Patch Product")
    def test_patch_product_partial(self, api):
        payload = {"title": "Patched Title", "price": 19.99}
        response = api.patch("/products/1", json=payload)
        assert response.status_code == 200
        product = response.json()
        assert product["title"] == payload["title"]
        assert product["price"] == payload["price"]


@pytest.mark.api
@allure.feature("Products")
class TestProductsDelete:
    """Tests for DELETE /products endpoint."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Delete Product")
    def test_delete_product(self, api):
        response = api.delete("/products/1")
        assert response.status_code == 200

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Delete Product")
    def test_delete_product_returns_data(self, api):
        response = api.delete("/products/1")
        assert response.status_code == 200
        product = response.json()
        assert "id" in product
