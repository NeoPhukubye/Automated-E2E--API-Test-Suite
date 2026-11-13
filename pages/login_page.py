from pages.base_page import BasePage
from config.settings import UI_BASE_URL
from typing import Optional, Literal


class LoginPage(BasePage):
    """Page object for the Sauce Demo login page."""

    URL = UI_BASE_URL
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = "[data-test='error']"

    def navigate(
        self,
        path: str = "",
        wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "domcontentloaded",
        timeout: Optional[int] = None,
    ) -> None:
        super().navigate(self.URL, wait_until=wait_until, timeout=timeout)

    def login(self, username: str, password: str):
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)
