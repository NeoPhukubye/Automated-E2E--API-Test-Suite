import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.product_page import ProductPage
from pages.checkout_page import CheckoutPage

STANDARD_USER = "standard_user"
STANDARD_PASSWORD = "secret_sauce"


@pytest.fixture()
def login_page(page):
    """Provide a LoginPage instance."""
    return LoginPage(page)


@pytest.fixture()
def home_page(page):
    """Provide a HomePage instance."""
    return HomePage(page)


@pytest.fixture()
def cart_page(page):
    """Provide a CartPage instance."""
    return CartPage(page)


@pytest.fixture()
def product_page(page):
    """Provide a ProductPage instance."""
    return ProductPage(page)


@pytest.fixture()
def checkout_page(page):
    """Provide a CheckoutPage instance."""
    return CheckoutPage(page)


@pytest.fixture()
def logged_in_page(page):
    """Provide a page that is already logged in as standard_user."""
    login = LoginPage(page)
    login.navigate()
    login.login(STANDARD_USER, STANDARD_PASSWORD)
    page.wait_for_url("**/inventory.html")
    return page
