import pytest
import allure
from pages.home_page import HomePage


@pytest.mark.e2e
@allure.feature("Product Display")
class TestSortingAndFilters:
    """E2E tests for product sorting edge cases and display behavior."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Default Sort")
    def test_default_sort_is_a_to_z(self, logged_in_page):
        """Verify default product order is alphabetical A-Z."""
        home = HomePage(logged_in_page)
        names = home.get_product_names()
        assert names == sorted(names)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Sort Persistence")
    def test_sort_resets_after_product_view(self, logged_in_page):
        """Verify sort order resets to default (A-Z) after viewing a product and returning."""
        from pages.product_page import ProductPage
        home = HomePage(logged_in_page)
        home.sort_products("hilo")
        home.click_product(0)
        product = ProductPage(logged_in_page)
        product.go_back()
        names_after = home.get_product_names()
        assert names_after == sorted(names_after)

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Price Format")
    def test_all_prices_are_valid_numbers(self, logged_in_page):
        """Verify all displayed prices can be parsed as float values."""
        home = HomePage(logged_in_page)
        prices = home.get_product_prices()
        for price in prices:
            numeric = float(price.replace("$", ""))
            assert numeric > 0

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Sort Toggle")
    def test_sort_low_high_then_high_low(self, logged_in_page):
        """Verify switching sort directions reverses product order."""
        home = HomePage(logged_in_page)
        home.sort_products("lohi")
        prices_asc = home.get_product_prices()
        home.sort_products("hilo")
        prices_desc = home.get_product_prices()
        assert prices_asc == list(reversed(prices_desc))

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Sort Toggle")
    def test_sort_a_z_then_z_a(self, logged_in_page):
        """Verify switching name sort directions reverses name order."""
        home = HomePage(logged_in_page)
        home.sort_products("az")
        names_asc = home.get_product_names()
        home.sort_products("za")
        names_desc = home.get_product_names()
        assert names_asc == list(reversed(names_desc))

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Product Count")
    def test_product_count_consistent_across_sorts(self, logged_in_page):
        """Verify product count doesn't change when sorting."""
        home = HomePage(logged_in_page)
        for sort_option in ["az", "za", "lohi", "hilo"]:
            home.sort_products(sort_option)
            assert home.get_product_count() == 6

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Product Images")
    def test_all_products_have_images(self, logged_in_page):
        """Verify every product card has an image element."""
        images = logged_in_page.locator(".inventory_item img")
        assert images.count() == 6
        for i in range(images.count()):
            src = images.nth(i).get_attribute("src")
            assert src and len(src) > 0
