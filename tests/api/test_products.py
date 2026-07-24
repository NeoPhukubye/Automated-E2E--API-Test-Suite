import pytest


@pytest.mark.api
@pytest.mark.smoke
class TestProducts:
    """Tests for the /products endpoint."""

    def test_get_all_products(self, api):
        response = api.get("/products")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) > 0

    def test_get_single_product(self, api):
        response = api.get("/products/1")
        assert response.status_code == 200
        product = response.json()
        assert product["id"] == 1
        assert "title" in product
        assert "price" in product
        assert "category" in product
        assert "description" in product
        assert "image" in product

    def test_get_product_categories(self, api):
        response = api.get("/products/categories")
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_get_products_by_category(self, api):
        response = api.get("/products/category/electronics")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        for product in products:
            assert product["category"] == "electronics"

    def test_get_products_with_limit(self, api):
        response = api.get("/products", params={"limit": 5})
        assert response.status_code == 200
        products = response.json()
        assert len(products) == 5
