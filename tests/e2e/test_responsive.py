import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage


@pytest.mark.e2e
@allure.feature("Responsive Design")
class TestResponsive:
    """E2E tests for layout behavior across different viewport sizes."""

    VIEWPORTS = [
        (1920, 1080, "desktop"),
        (1024, 768, "tablet_landscape"),
        (768, 1024, "tablet_portrait"),
        (375, 812, "mobile"),
    ]

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Desktop Layout")
    def test_desktop_layout(self, page):
        """Verify products display correctly at desktop resolution."""
        page.set_viewport_size({"width": 1920, "height": 1080})
        self._login_and_verify(page)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Tablet Layout")
    def test_tablet_landscape_layout(self, page):
        """Verify products display correctly at tablet landscape resolution."""
        page.set_viewport_size({"width": 1024, "height": 768})
        self._login_and_verify(page)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Tablet Layout")
    def test_tablet_portrait_layout(self, page):
        """Verify products display correctly at tablet portrait resolution."""
        page.set_viewport_size({"width": 768, "height": 1024})
        self._login_and_verify(page)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Mobile Layout")
    def test_mobile_layout(self, page):
        """Verify products display correctly at mobile resolution."""
        page.set_viewport_size({"width": 375, "height": 812})
        self._login_and_verify(page)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Mobile Layout")
    def test_burger_menu_clickable_on_mobile(self, page):
        """Verify the burger menu is interactive on mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 812})
        login = LoginPage(page)
        login.navigate()
        login.login("standard_user", "secret_sauce")
        page.wait_for_url("**/inventory.html")
        page.locator("#react-burger-menu-btn").click()
        assert page.locator(".bm-menu").is_visible()

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Cart Accessibility")
    def test_cart_accessible_all_viewports(self, page):
        """Verify cart link is visible at all viewport sizes."""
        for width, height, _ in self.VIEWPORTS:
            page.set_viewport_size({"width": width, "height": height})
            login = LoginPage(page)
            login.navigate()
            login.login("standard_user", "secret_sauce")
            page.wait_for_url("**/inventory.html")
            assert page.locator(".shopping_cart_link").is_visible()
            page.goto("about:blank")

    def _login_and_verify(self, page):
        """Helper to login and verify products are visible."""
        login = LoginPage(page)
        login.navigate()
        login.login("standard_user", "secret_sauce")
        page.wait_for_url("**/inventory.html")
        home = HomePage(page)
        assert home.get_product_count() == 6
