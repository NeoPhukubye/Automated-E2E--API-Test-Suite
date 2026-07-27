import pytest
import allure
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from utils.test_data import TestDataGenerator


@pytest.mark.e2e
@allure.feature("Checkout")
class TestCheckoutValidation:
    """E2E tests for checkout form validation and edge cases."""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Required Fields")
    def test_missing_first_name(self, logged_in_page):
        """Verify error when first name is empty."""
        self._go_to_checkout(logged_in_page)
        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("", "Doe", "12345")
        checkout.continue_checkout()
        assert checkout.is_error_displayed()
        assert "First Name is required" in checkout.get_error_message()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Required Fields")
    def test_missing_last_name(self, logged_in_page):
        """Verify error when last name is empty."""
        self._go_to_checkout(logged_in_page)
        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "", "12345")
        checkout.continue_checkout()
        assert checkout.is_error_displayed()
        assert "Last Name is required" in checkout.get_error_message()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Required Fields")
    def test_missing_postal_code(self, logged_in_page):
        """Verify error when postal code is empty."""
        self._go_to_checkout(logged_in_page)
        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "Doe", "")
        checkout.continue_checkout()
        assert checkout.is_error_displayed()
        assert "Postal Code is required" in checkout.get_error_message()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Valid Submission")
    def test_checkout_with_generated_data(self, logged_in_page):
        """Verify checkout works with randomly generated valid data."""
        data = TestDataGenerator()
        self._go_to_checkout(logged_in_page)
        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info(
            data.first_name(), data.last_name(), data.postal_code()
        )
        checkout.continue_checkout()
        assert "Checkout: Overview" in checkout.get_page_title()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Cancel Flow")
    def test_cancel_returns_to_cart(self, logged_in_page):
        """Verify cancel button returns to cart page."""
        self._go_to_checkout(logged_in_page)
        checkout = CheckoutPage(logged_in_page)
        checkout.cancel()
        assert "/cart.html" in logged_in_page.url

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Order Summary")
    def test_checkout_overview_shows_total(self, logged_in_page):
        """Verify checkout overview displays a total price."""
        self._go_to_checkout(logged_in_page)
        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "Doe", "12345")
        checkout.continue_checkout()
        total = checkout.get_total()
        assert "Total:" in total

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("Order Completion")
    def test_order_confirmation_page(self, logged_in_page):
        """Verify order confirmation displays success message."""
        self._go_to_checkout(logged_in_page)
        checkout = CheckoutPage(logged_in_page)
        checkout.fill_shipping_info("John", "Doe", "12345")
        checkout.continue_checkout()
        checkout.finish_checkout()
        assert "Thank you for your order" in checkout.get_complete_header()
        assert "/checkout-complete.html" in logged_in_page.url

    def _go_to_checkout(self, page):
        """Helper to navigate from inventory to checkout."""
        home = HomePage(page)
        home.add_item_to_cart(0)
        home.go_to_cart()
        cart = CartPage(page)
        cart.proceed_to_checkout()
