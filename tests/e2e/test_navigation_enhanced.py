"""Tests for navigation and menu interactions."""

import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.cart_page import CartPage


@pytest.mark.e2e
@allure.feature("Navigation")
class TestNavigationEnhanced:
    """Enhanced E2E tests for navigation and menu interactions."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Burger Menu")
    def test_burger_menu_opens(self, logged_in_page):
        """Verify burger menu opens and displays options."""
        home = HomePage(logged_in_page)
        home.click_burger_menu()
        assert home.is_burger_menu_visible()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Burger Menu")
    def test_burger_menu_has_all_links(self, logged_in_page):
        """Verify burger menu contains all navigation links."""
        home = HomePage(logged_in_page)
        home.click_burger_menu()
        links = home.get_burger_menu_links()
        assert "inventory" in links
        assert "cart" in links
        assert "checkout" in links
        assert "logout" in links

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Navigation")
    def test_navigation_to_cart_from_menu(self, logged_in_page):
        """Verify navigation to cart from burger menu."""
        home = HomePage(logged_in_page)
        home.click_burger_menu()
        home.click_burger_menu_link("cart")
        assert "/cart.html" in logged_in_page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Navigation")
    def test_navigation_to_inventory_from_menu(self, logged_in_page):
        """Verify navigation to inventory from burger menu."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.click_burger_menu()
        home.click_burger_menu_link("inventory")
        assert "/inventory.html" in logged_in_page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Navigation")
    def test_logout_from_menu(self, logged_in_page):
        """Verify logout from burger menu returns to login page."""
        home = HomePage(logged_in_page)
        home.click_burger_menu()
        home.click_logout()
        assert "/inventory.html" not in logged_in_page.url
        assert logged_in_page.url.rstrip("/") == "https://www.saucedemo.com"

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Cart Icon Navigation")
    def test_cart_icon_navigates_to_cart(self, logged_in_page):
        """Verify clicking cart icon navigates to cart page."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.click_cart_icon()
        assert "/cart.html" in logged_in_page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Page Title")
    def test_inventory_page_title(self, logged_in_page):
        """Verify inventory page title is 'Products'."""
        home = HomePage(logged_in_page)
        assert home.get_page_title() == "Products"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Page Title")
    def test_cart_page_title(self, logged_in_page):
        """Verify cart page title is 'Your Cart'."""
        home = HomePage(logged_in_page)
        home.go_to_cart()
        cart = CartPage(logged_in_page)
        assert cart.get_page_title() == "Your Cart"

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Footer")
    def test_footer_visible(self, logged_in_page):
        """Verify footer is visible on inventory page."""
        home = HomePage(logged_in_page)
        assert home.is_footer_visible()

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Social Media Links")
    def test_footer_social_links(self, logged_in_page):
        """Verify footer social media links are present."""
        home = HomePage(logged_in_page)
        assert home.get_social_link_count() >= 3