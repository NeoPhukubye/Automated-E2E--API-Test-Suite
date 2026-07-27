from pages.base_page import BasePage
from config.settings import UI_BASE_URL


class CheckoutPage(BasePage):
    """Page object for the Sauce Demo checkout pages."""

    URL = f"{UI_BASE_URL}/checkout-step-one.html"
    FIRST_NAME_INPUT = "#first-name"
    LAST_NAME_INPUT = "#last-name"
    POSTAL_CODE_INPUT = "#postal-code"
    CONTINUE_BUTTON = "#continue"
    CANCEL_BUTTON = "#cancel"
    FINISH_BUTTON = "#finish"
    ERROR_MESSAGE = "[data-test='error']"
    SUMMARY_TOTAL = ".summary_total_label"
    COMPLETE_HEADER = ".complete-header"
    PAGE_TITLE = ".title"

    def navigate(self, path: str = ""):
        super().navigate(self.URL)

    def fill_shipping_info(self, first_name: str, last_name: str, postal_code: str):
        self.fill(self.FIRST_NAME_INPUT, first_name)
        self.fill(self.LAST_NAME_INPUT, last_name)
        self.fill(self.POSTAL_CODE_INPUT, postal_code)

    def continue_checkout(self):
        self.click(self.CONTINUE_BUTTON)

    def finish_checkout(self):
        self.click(self.FINISH_BUTTON)

    def cancel(self):
        self.click(self.CANCEL_BUTTON)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)

    def get_total(self) -> str:
        return self.get_text(self.SUMMARY_TOTAL)

    def get_complete_header(self) -> str:
        return self.get_text(self.COMPLETE_HEADER)

    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)
