import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.cart_page import CartPage


@pytest.mark.e2e
class TestNavigation:
    """E2E tests for site navigation and page transitions."""

    def test_unauthenticated_redirect(self, page):
        """Verify unauthenticated users see the login page when accessing protected routes."""
        from config.settings import UI_BASE_URL
        page.goto(f"{UI_BASE_URL}/inventory.html")
        page.wait_for_load_state("networkidle")
        is_on_login = page.url.rstrip("/") == UI_BASE_URL
        has_login_form = page.locator("#login-button").is_visible()
        has_error = page.locator("[data-test='error']").is_visible()
        assert is_on_login or has_login_form or has_error, (
            f"Expected login page or error, but got {page.url}"
        )

    def test_cart_page_title(self, logged_in_page):
        """Verify cart page displays correct title."""
        home = HomePage(logged_in_page)
        home.go_to_cart()
        cart = CartPage(logged_in_page)
        assert cart.get_page_title() == "Your Cart"

    def test_back_from_product_detail(self, logged_in_page):
        """Verify back button returns to inventory from product detail."""
        from pages.product_page import ProductPage
        home = HomePage(logged_in_page)
        home.click_product(0)
        product = ProductPage(logged_in_page)
        product.go_back()
        assert "/inventory.html" in logged_in_page.url

    def test_burger_menu_visible(self, logged_in_page):
        """Verify the hamburger menu button is present."""
        home = HomePage(logged_in_page)
        assert home.is_visible(home.BURGER_MENU)

    def test_cart_icon_always_visible(self, logged_in_page):
        """Verify the shopping cart icon is always visible."""
        home = HomePage(logged_in_page)
        assert home.is_visible(home.SHOPPING_CART_LINK)

    def test_logout(self, logged_in_page):
        """Verify user can log out via burger menu."""
        from config.settings import UI_BASE_URL
        logged_in_page.locator("#react-burger-menu-btn").click()
        logged_in_page.locator("#logout_sidebar_link").click()
        assert logged_in_page.url.rstrip("/") == UI_BASE_URL
