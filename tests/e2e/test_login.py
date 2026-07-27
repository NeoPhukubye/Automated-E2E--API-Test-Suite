import pytest
from pages.login_page import LoginPage


@pytest.mark.e2e
class TestLogin:
    """E2E tests for the login functionality."""

    STANDARD_USER = "standard_user"
    LOCKED_USER = "locked_out_user"
    PASSWORD = "secret_sauce"

    def test_successful_login(self, login_page):
        """Verify standard user can log in successfully."""
        login_page.navigate()
        login_page.login(self.STANDARD_USER, self.PASSWORD)
        assert "/inventory.html" in login_page.get_url()

    def test_locked_out_user(self, login_page):
        """Verify locked out user sees an error message."""
        login_page.navigate()
        login_page.login(self.LOCKED_USER, self.PASSWORD)
        assert login_page.is_error_displayed()
        assert "locked out" in login_page.get_error_message().lower()

    def test_invalid_credentials(self, login_page):
        """Verify invalid credentials show an error."""
        login_page.navigate()
        login_page.login("invalid_user", "wrong_password")
        assert login_page.is_error_displayed()
        assert "Username and password" in login_page.get_error_message()

    def test_empty_username(self, login_page):
        """Verify empty username shows validation error."""
        login_page.navigate()
        login_page.login("", self.PASSWORD)
        assert login_page.is_error_displayed()
        assert "Username is required" in login_page.get_error_message()

    def test_empty_password(self, login_page):
        """Verify empty password shows validation error."""
        login_page.navigate()
        login_page.login(self.STANDARD_USER, "")
        assert login_page.is_error_displayed()
        assert "Password is required" in login_page.get_error_message()
