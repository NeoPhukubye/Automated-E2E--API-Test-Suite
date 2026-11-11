"""Tests for product detail page functionality."""

import pytest
import allure
from pages.home_page import HomePage
from pages.product_page import ProductPage


@pytest.mark.e2e
@allure.feature("Product Details")
class TestProductDetail:
    """E2E tests for product detail page interactions."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Product Detail Display")
    def test_product_detail_displays_name(self, logged_in_page):
        """Verify product detail page shows product name."""
        home = HomePage(logged_in_page)
        product_name = home.get_product_names()[0]
        home.click_product(0)
        product = ProductPage(logged_in_page)
        assert product_name in product.get_product_name()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Product Detail Display")
    def test_product_detail_displays_price(self, logged_in_page):
        """Verify product detail page shows product price."""
        home = HomePage(logged_in_page)
        home.click_product(0)
        product = ProductPage(logged_in_page)
        price = product.get_price()
        assert price.startswith("$")
        assert float(price.replace("$", "")) > 0

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Product Detail Display")
    def test_product_detail_displays_description(self, logged_in_page):
        """Verify product detail page shows product description."""
        home = HomePage(logged_in_page)
        home.click_product(0)
        product = ProductPage(logged_in_page)
        description = product.get_description()
        assert len(description.strip()) > 0

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Product Detail Display")
    def test_product_detail_displays_image(self, logged_in_page):
        """Verify product detail page shows product image."""
        home = HomePage(logged_in_page)
        home.click_product(0)
        product = ProductPage(logged_in_page)
        src = product.get_image_src()
        assert src and len(src) > 0

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Add to Cart from Detail")
    def test_add_to_cart_from_detail(self, logged_in_page):
        """Verify adding item from product detail page updates cart badge."""
        home = HomePage(logged_in_page)
        home.click_product(0)
        product = ProductPage(logged_in_page)
        product.add_to_cart()
        assert home.is_cart_badge_visible()
        assert home.get_cart_badge_count() == "1"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Back Navigation")
    def test_back_returns_to_inventory(self, logged_in_page):
        """Verify back button returns to inventory page."""
        home = HomePage(logged_in_page)
        home.click_product(0)
        product = ProductPage(logged_in_page)
        product.go_back()
        assert "/inventory.html" in logged_in_page.url
        assert home.get_product_count() == 6

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Product Detail URL")
    def test_product_detail_url_contains_item(self, logged_in_page):
        """Verify product detail URL contains inventory-item."""
        home = HomePage(logged_in_page)
        home.click_product(0)
        assert "/inventory-item.html" in logged_in_page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Multiple Products")
    def test_different_products_have_different_details(self, logged_in_page):
        """Verify different products show different names."""
        home = HomePage(logged_in_page)
        name1 = home.get_product_names()[0]
        name2 = home.get_product_names()[1]
        assert name1 != name2

        home.click_product(0)
        product1 = ProductPage(logged_in_page)
        detail_name1 = product1.get_product_name()

        product1.go_back()
        home.click_product(1)
        product2 = ProductPage(logged_in_page)
        detail_name2 = product2.get_product_name()

        assert detail_name1 == name1
        assert detail_name2 == name2