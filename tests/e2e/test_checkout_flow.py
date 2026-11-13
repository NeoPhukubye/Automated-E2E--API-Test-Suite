"""Tests for checkout flow and order confirmation."""

import pytest
import allure
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


@pytest.mark.e2e
@allure.feature("Checkout")
class TestCheckoutFlow:
    """E2E tests for complete checkout flow."""

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("Order Completion")
    def test_complete_checkout_with_valid_info(self, logged_in_page):
        """Verify complete checkout with valid information."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.go_to_cart()

        cart = CartPage(logged_in_page)
        cart.proceed_to_checkout()

        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "Doe", "12345")
        checkout.continue_checkout()
        checkout.finish_checkout()

        assert "Thank you for your order" in checkout.get_complete_header()
        assert "/checkout-complete.html" in logged_in_page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Order Summary")
    def test_checkout_overview_shows_items(self, logged_in_page):
        """Verify checkout overview displays added items."""
        home = HomePage(logged_in_page)
        product_name = home.get_product_names()[0]
        home.add_item_to_cart(0)
        home.go_to_cart()

        cart = CartPage(logged_in_page)
        cart.proceed_to_checkout()

        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("Jane", "Doe", "67890")
        checkout.continue_checkout()

        assert product_name in checkout.get_item_labels()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Order Summary")
    def test_checkout_overview_shows_total(self, logged_in_page):
        """Verify checkout overview displays total price."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.go_to_cart()

        cart = CartPage(logged_in_page)
        cart.proceed_to_checkout()

        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "Doe", "12345")
        checkout.continue_checkout()

        total = checkout.get_total()
        assert "Total:" in total

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Cancel Flow")
    def test_cancel_checkout_returns_to_cart(self, logged_in_page):
        """Verify cancel button on checkout returns to cart."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.go_to_cart()

        cart = CartPage(logged_in_page)
        cart.proceed_to_checkout()

        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "Doe", "12345")
        checkout.cancel()

        assert "/cart.html" in logged_in_page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Cancel Flow")
    def test_cancel_from_overview_returns_to_cart(self, logged_in_page):
        """Verify cancel button on overview returns to cart."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.go_to_cart()

        cart = CartPage(logged_in_page)
        cart.proceed_to_checkout()

        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "Doe", "12345")
        checkout.continue_checkout()
        checkout.cancel()

        assert "/cart.html" in logged_in_page.url

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Multiple Items Checkout")
    def test_checkout_with_multiple_items(self, logged_in_page):
        """Verify checkout with multiple items shows correct totals."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.add_item_to_cart(1)
        home.add_item_to_cart(2)
        home.go_to_cart()

        cart = CartPage(logged_in_page)
        assert cart.get_cart_item_count() == 3
        cart.proceed_to_checkout()

        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "Doe", "12345")
        checkout.continue_checkout()

        assert checkout.get_item_count() == 3

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Payment Info")
    def test_checkout_overview_has_payment_info(self, logged_in_page):
        """Verify checkout overview shows payment and shipping info."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.go_to_cart()

        cart = CartPage(logged_in_page)
        cart.proceed_to_checkout()

        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "Doe", "12345")
        checkout.continue_checkout()

        assert checkout.get_payment_info() is not None
        assert checkout.get_shipping_info() is not None
