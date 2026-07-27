import pytest
from pages.home_page import HomePage


@pytest.mark.e2e
class TestProductBrowsing:
    """E2E tests for browsing products on the inventory page."""

    def test_products_are_displayed(self, logged_in_page):
        """Verify products are listed on the home page."""
        home = HomePage(logged_in_page)
        assert home.get_product_count() == 6

    def test_product_names_visible(self, logged_in_page):
        """Verify all product names are non-empty."""
        home = HomePage(logged_in_page)
        names = home.get_product_names()
        assert len(names) == 6
        assert all(name.strip() for name in names)

    def test_product_prices_visible(self, logged_in_page):
        """Verify all product prices start with dollar sign."""
        home = HomePage(logged_in_page)
        prices = home.get_product_prices()
        assert len(prices) == 6
        assert all(price.startswith("$") for price in prices)

    def test_sort_by_price_low_to_high(self, logged_in_page):
        """Verify sorting by price low-to-high orders products correctly."""
        home = HomePage(logged_in_page)
        home.sort_products("lohi")
        prices = home.get_product_prices()
        numeric_prices = [float(p.replace("$", "")) for p in prices]
        assert numeric_prices == sorted(numeric_prices)

    def test_sort_by_price_high_to_low(self, logged_in_page):
        """Verify sorting by price high-to-low orders products correctly."""
        home = HomePage(logged_in_page)
        home.sort_products("hilo")
        prices = home.get_product_prices()
        numeric_prices = [float(p.replace("$", "")) for p in prices]
        assert numeric_prices == sorted(numeric_prices, reverse=True)

    def test_sort_by_name_a_to_z(self, logged_in_page):
        """Verify sorting by name A-Z orders products alphabetically."""
        home = HomePage(logged_in_page)
        home.sort_products("az")
        names = home.get_product_names()
        assert names == sorted(names)

    def test_sort_by_name_z_to_a(self, logged_in_page):
        """Verify sorting by name Z-A orders products reverse alphabetically."""
        home = HomePage(logged_in_page)
        home.sort_products("za")
        names = home.get_product_names()
        assert names == sorted(names, reverse=True)

    def test_click_product_opens_detail(self, logged_in_page):
        """Verify clicking a product navigates to its detail page."""
        home = HomePage(logged_in_page)
        first_product_name = home.get_product_names()[0]
        home.click_product(0)
        assert "/inventory-item.html" in home.get_url()

    def test_page_title_is_products(self, logged_in_page):
        """Verify the inventory page title says Products."""
        home = HomePage(logged_in_page)
        assert home.get_page_title() == "Products"
