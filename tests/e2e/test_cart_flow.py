import pytest
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


@pytest.mark.e2e
class TestCartFlow:
    """E2E tests for the shopping cart workflow."""

    def test_add_item_to_cart(self, logged_in_page):
        """Verify adding an item updates the cart badge."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        assert home.is_cart_badge_visible()
        assert home.get_cart_badge_count() == "1"

    def test_add_multiple_items(self, logged_in_page):
        """Verify adding multiple items increments the badge."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.add_item_to_cart(1)
        assert home.get_cart_badge_count() == "2"

    def test_remove_item_from_home(self, logged_in_page):
        """Verify removing an item from home page decrements badge."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.remove_item_from_cart(0)
        assert not home.is_cart_badge_visible()

    def test_cart_shows_added_items(self, logged_in_page):
        """Verify cart page displays the correct items."""
        home = HomePage(logged_in_page)
        product_name = home.get_product_names()[0]
        home.add_item_to_cart(0)
        home.go_to_cart()
        cart = CartPage(logged_in_page)
        assert cart.get_cart_item_count() == 1
        assert product_name in cart.get_cart_item_names()

    def test_remove_item_from_cart_page(self, logged_in_page):
        """Verify removing an item from the cart page works."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.go_to_cart()
        cart = CartPage(logged_in_page)
        cart.remove_item(0)
        assert cart.get_cart_item_count() == 0

    def test_continue_shopping_returns_to_inventory(self, logged_in_page):
        """Verify continue shopping navigates back to products."""
        home = HomePage(logged_in_page)
        home.go_to_cart()
        cart = CartPage(logged_in_page)
        cart.continue_shopping()
        assert "/inventory.html" in logged_in_page.url

    def test_full_checkout_flow(self, logged_in_page):
        """Verify complete purchase flow from cart to order confirmation."""
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

    def test_checkout_requires_info(self, logged_in_page):
        """Verify checkout shows error if info is missing."""
        home = HomePage(logged_in_page)
        home.add_item_to_cart(0)
        home.go_to_cart()

        cart = CartPage(logged_in_page)
        cart.proceed_to_checkout()

        checkout = CheckoutPage(logged_in_page)
        checkout.continue_checkout()

        assert checkout.is_error_displayed()
