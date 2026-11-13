"""E2E test fixtures for Sauce Demo browser tests."""

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
LOCKED_USER = "locked_out_user"
PROBLEM_USER = "problem_user"
PERFORMANCE_GLITCH_USER = "performance_glitch_user"
ERROR_USER = "error_user"
VISUAL_USER = "visual_user"


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
    HomePage(page).wait_until_ready()
    return page


@pytest.fixture()
def logged_in_problem_user(page):
    """Provide a page logged in as problem_user (has UI bugs)."""
    login = LoginPage(page)
    login.navigate()
    login.login(PROBLEM_USER, STANDARD_PASSWORD)
    page.wait_for_url("**/inventory.html")
    HomePage(page).wait_until_ready()
    return page


@pytest.fixture()
def logged_in_performance_glitch_user(page):
    """Provide a page logged in as performance_glitch_user (slow)."""
    login = LoginPage(page)
    login.navigate()
    login.login(PERFORMANCE_GLITCH_USER, STANDARD_PASSWORD)
    page.wait_for_url("**/inventory.html")
    HomePage(page).wait_until_ready()
    return page


@pytest.fixture()
def page_with_item(logged_in_page):
    """Provide a page with one item already added to the cart."""
    home = HomePage(logged_in_page)
    home.add_item_to_cart(0)
    home.page.locator(home.SHOPPING_CART_BADGE).first.wait_for(state="visible")
    return logged_in_page


@pytest.fixture()
def page_with_multiple_items(logged_in_page):
    """Provide a page with multiple items already added to the cart."""
    home = HomePage(logged_in_page)
    for i in range(3):
        home.add_item_to_cart(i)
    home.page.locator(home.SHOPPING_CART_BADGE).first.wait_for(state="visible")
    return logged_in_page


@pytest.fixture()
def checkout_info() -> dict:
    """Provide valid checkout information."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "postal_code": "12345",
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure and attach to Allure report."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = (
            item.funcargs.get("page")
            or item.funcargs.get("logged_in_page")
            or item.funcargs.get("logged_in_problem_user")
            or item.funcargs.get("logged_in_performance_glitch_user")
        )
        if page:
            screenshot_dir = "reports/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(
                screenshot_dir,
                f"{item.nodeid.replace('::', '_').replace('/', '_')}.png",
            )
            page.screenshot(path=screenshot_path)
            allure.attach.file(
                screenshot_path,
                name="failure_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
