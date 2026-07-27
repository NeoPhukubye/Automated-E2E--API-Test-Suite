import os
import pytest
import allure
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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure and attach to Allure report."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
        if page:
            screenshot_dir = "reports/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(
                screenshot_dir, f"{item.nodeid.replace('::', '_').replace('/', '_')}.png"
            )
            page.screenshot(path=screenshot_path)
            allure.attach.file(
                screenshot_path,
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
