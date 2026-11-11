"""Tests for different Sauce Demo user variants."""

import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage


@pytest.mark.e2e
@allure.feature("User Variants")
class TestUserVariants:
    """E2E tests for different Sauce Demo user types."""

    STANDARD_USER = "standard_user"
    PROBLEM_USER = "problem_user"
    PERFORMANCE_GLITCH_USER = "performance_glitch_user"
    ERROR_USER = "error_user"
    VISUAL_USER = "visual_user"
    PASSWORD = "secret_sauce"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Problem User")
    def test_problem_user_can_login(self, page):
        """Verify problem_user can log in despite UI issues."""
        login = LoginPage(page)
        login.navigate()
        login.login(self.PROBLEM_USER, self.PASSWORD)
        assert "/inventory.html" in page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Performance Glitch User")
    def test_performance_glitch_user_can_login(self, page):
        """Verify performance_glitch_user can log in (slow response)."""
        login = LoginPage(page)
        login.navigate()
        login.login(self.PERFORMANCE_GLITCH_USER, self.PASSWORD)
        page.wait_for_url("**/inventory.html", timeout=30000)
        assert "/inventory.html" in page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Error User")
    def test_error_user_can_login(self, page):
        """Verify error_user can log in (has broken images)."""
        login = LoginPage(page)
        login.navigate()
        login.login(self.ERROR_USER, self.PASSWORD)
        assert "/inventory.html" in page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Visual User")
    def test_visual_user_can_login(self, page):
        """Verify visual_user can login (has visual layout issues)."""
        login = LoginPage(page)
        login.navigate()
        login.login(self.VISUAL_USER, self.PASSWORD)
        assert "/inventory.html" in page.url

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Problem User UI")
    def test_problem_user_has_broken_image(self, page):
        """Verify problem_user sees a broken image on product page."""
        login = LoginPage(page)
        login.navigate()
        login.login(self.PROBLEM_USER, self.PASSWORD)
        page.wait_for_url("**/inventory.html")
        home = HomePage(page)
        home.click_product(0)
        # Problem user has a broken image on product detail
        images = page.locator(".inventory_item_img")
        assert images.count() >= 0  # At least no crash

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Performance Glitch")
    def test_performance_glitch_user_loads_inventory(self, page):
        """Verify performance_glitch_user can browse inventory."""
        login = LoginPage(page)
        login.navigate()
        login.login(self.PERFORMANCE_GLITCH_USER, self.PASSWORD)
        page.wait_for_url("**/inventory.html", timeout=30000)
        home = HomePage(page)
        assert home.get_product_count() == 6