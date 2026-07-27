from playwright.sync_api import Page, expect


class BasePage:
    """Base page object providing shared browser interactions."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, path: str = ""):
        self.page.goto(path)

    def get_title(self) -> str:
        return self.page.title()

    def get_url(self) -> str:
        return self.page.url

    def wait_for_load(self):
        self.page.wait_for_load_state("networkidle")

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).text_content() or ""

    def click(self, selector: str):
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str):
        self.page.locator(selector).fill(value)
