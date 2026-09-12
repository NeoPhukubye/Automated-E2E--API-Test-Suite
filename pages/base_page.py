"""Base page object providing shared browser interactions for E2E tests."""

from typing import Optional
from playwright.sync_api import Page, Locator, expect


class BasePage:
    """Base page object providing shared browser interactions."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, path: str = ""):
        """Navigate to the given path."""
        self.page.goto(path)

    def get_title(self) -> str:
        """Return the page title."""
        return self.page.title()

    def get_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    def wait_for_load(self):
        """Wait for the page to reach network idle state."""
        self.page.wait_for_load_state("networkidle")

    def wait_for_url(self, pattern: str, timeout: Optional[int] = None):
        """Wait for the URL to match a glob pattern."""
        self.page.wait_for_url(pattern, timeout=timeout)

    def is_visible(self, selector: str) -> bool:
        """Check if an element is visible on the page."""
        return self.page.locator(selector).is_visible()

    def is_enabled(self, selector: str) -> bool:
        """Check if an element is enabled."""
        return self.page.locator(selector).is_enabled()

    def is_checked(self, selector: str) -> bool:
        """Check if a checkbox/radio is checked."""
        return self.page.locator(selector).is_checked()

    def get_text(self, selector: str) -> str:
        """Get the text content of an element."""
        return self.page.locator(selector).text_content() or ""

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get the value of an attribute on an element."""
        return self.page.locator(selector).get_attribute(attribute)

    def get_all_text(self, selector: str) -> list[str]:
        """Get text content of all elements matching the selector."""
        return self.page.locator(selector).all_text_contents()

    def click(self, selector: str):
        """Click an element by selector."""
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str):
        """Fill an input field with a value."""
        self.page.locator(selector).fill(value)

    def press(self, selector: str, key: str):
        """Press a keyboard key on an element."""
        self.page.locator(selector).press(key)

    def hover(self, selector: str):
        """Hover over an element."""
        self.page.locator(selector).hover()

    def select_option(self, selector: str, value: str):
        """Select an option from a dropdown."""
        self.page.locator(selector).select_option(value)

    def check(self, selector: str):
        """Check a checkbox."""
        self.page.locator(selector).check()

    def uncheck(self, selector: str):
        """Uncheck a checkbox."""
        self.page.locator(selector).uncheck()

    def wait_for_selector(self, selector: str, timeout: Optional[int] = None):
        """Wait for an element to appear in the DOM."""
        self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_selector_visible(self, selector: str, timeout: Optional[int] = None):
        """Wait for an element to become visible."""
        self.page.locator(selector).wait_for(state="visible", timeout=timeout)

    def expect_selector(self, selector: str) -> Locator:
        """Return a Playwright Locator for assertion-style tests."""
        return expect(self.page.locator(selector))

    def reload(self):
        """Reload the current page."""
        self.page.reload()

    def go_back(self):
        """Navigate back in browser history."""
        self.page.go_back()

    def go_forward(self):
        """Navigate forward in browser history."""
        self.page.go_forward()

    def screenshot(self, path: Optional[str] = None):
        """Take a screenshot of the current page."""
        return self.page.screenshot(path=path)