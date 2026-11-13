"""Base page object providing shared browser interactions for E2E tests."""

import logging
from typing import Optional, List, Any, Literal, Dict
from playwright.sync_api import (
    Page,
    expect,
    TimeoutError as PlaywrightTimeoutError,
)

from config.settings import TIMEOUT, SLOW_MO


logger = logging.getLogger(__name__)


class BasePage:
    """Base page object providing shared browser interactions."""

    DEFAULT_TIMEOUT = TIMEOUT * 1000  # Convert to milliseconds
    SLOW_MO = SLOW_MO

    def __init__(self, page: Page):
        self.page = page
        self._default_timeout = self.DEFAULT_TIMEOUT

    @property
    def default_timeout(self) -> int:
        """Get the default timeout in milliseconds."""
        return self._default_timeout

    @default_timeout.setter
    def default_timeout(self, value: int):
        """Set the default timeout in milliseconds."""
        self._default_timeout = value

    def navigate(
        self,
        path: str = "",
        wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "domcontentloaded",
        timeout: Optional[int] = None,
    ) -> None:
        """Navigate to the given path and wait for the specified load state.

        Args:
            path: URL path to navigate to
            wait_until: Load state to wait for ('load', 'domcontentloaded', 'networkidle', 'commit')
            timeout: Optional timeout in milliseconds
        """
        timeout = timeout or self._default_timeout
        logger.info(
            f"Navigating to: {path} (wait_until={wait_until}, timeout={timeout}ms)"
        )
        self.page.goto(path, wait_until=wait_until, timeout=timeout)

    def get_title(self) -> str:
        """Return the page title."""
        return self.page.title()

    def get_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    def wait_for_load(
        self,
        state: Literal["domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: Optional[int] = None,
    ) -> None:
        """Wait for the page to reach the specified load state."""
        timeout = timeout or self._default_timeout
        self.page.wait_for_load_state(state, timeout=timeout)

    def wait_for_url(
        self,
        pattern: str,
        timeout: Optional[int] = None,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "networkidle",
    ) -> None:
        """Wait for the URL to match a glob pattern."""
        timeout = timeout or self._default_timeout
        self.page.wait_for_url(pattern, timeout=timeout, wait_until=wait_until)

    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if an element is visible on the page."""
        try:
            return self.page.locator(selector).is_visible(
                timeout=timeout or self._default_timeout
            )
        except PlaywrightTimeoutError:
            return False

    def is_enabled(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if an element is enabled."""
        try:
            return self.page.locator(selector).is_enabled(
                timeout=timeout or self._default_timeout
            )
        except PlaywrightTimeoutError:
            return False

    def is_checked(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if a checkbox/radio is checked."""
        try:
            return self.page.locator(selector).is_checked(
                timeout=timeout or self._default_timeout
            )
        except PlaywrightTimeoutError:
            return False

    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """Get the text content of an element."""
        try:
            return (
                self.page.locator(selector).text_content(
                    timeout=timeout or self._default_timeout
                )
                or ""
            )
        except PlaywrightTimeoutError:
            return ""

    def get_attribute(
        self, selector: str, attribute: str, timeout: Optional[int] = None
    ) -> Optional[str]:
        """Get the value of an attribute on an element."""
        try:
            return self.page.locator(selector).get_attribute(
                attribute, timeout=timeout or self._default_timeout
            )
        except PlaywrightTimeoutError:
            return None

    def get_all_text(self, selector: str, timeout: Optional[int] = None) -> List[str]:
        """Get text content of all elements matching the selector."""
        try:
            locator = self.page.locator(selector)
            if timeout:
                locator.wait_for(state="attached", timeout=timeout)
            return locator.all_text_contents()
        except PlaywrightTimeoutError:
            return []

    def click(self, selector: str, timeout: Optional[int] = None, force: bool = False):
        """Click an element by selector, waiting for visibility first."""
        timeout = timeout or self._default_timeout
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        locator.click(timeout=timeout, force=force)

    def fill(self, selector: str, value: str, timeout: Optional[int] = None):
        """Fill an input field with a value, waiting for visibility first."""
        timeout = timeout or self._default_timeout
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        locator.fill(value, timeout=timeout)

    def press(self, selector: str, key: str, timeout: Optional[int] = None):
        """Press a keyboard key on an element."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).press(key, timeout=timeout)

    def hover(self, selector: str, timeout: Optional[int] = None):
        """Hover over an element."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).hover(timeout=timeout)

    def select_option(self, selector: str, value: str, timeout: Optional[int] = None):
        """Select an option from a dropdown."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).select_option(value, timeout=timeout)

    def check(self, selector: str, timeout: Optional[int] = None):
        """Check a checkbox."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).check(timeout=timeout)

    def uncheck(self, selector: str, timeout: Optional[int] = None):
        """Uncheck a checkbox."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).uncheck(timeout=timeout)

    def wait_for_selector(
        self,
        selector: str,
        state: Literal["attached", "detached", "hidden", "visible"] = "attached",
        timeout: Optional[int] = None,
    ) -> None:
        """Wait for an element to reach a specific state."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).wait_for(state=state, timeout=timeout)

    def wait_for_selector_visible(self, selector: str, timeout: Optional[int] = None):
        """Wait for an element to become visible."""
        self.wait_for_selector(selector, state="visible", timeout=timeout)

    def wait_for_selector_hidden(self, selector: str, timeout: Optional[int] = None):
        """Wait for an element to become hidden."""
        self.wait_for_selector(selector, state="hidden", timeout=timeout)

    def expect_selector(self, selector: str) -> Any:
        """Return a Playwright Locator for assertion-style tests."""
        return expect(self.page.locator(selector))

    def expect_visible(self, selector: str, timeout: Optional[int] = None) -> None:
        """Assert an element is visible."""
        timeout = timeout or self._default_timeout
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    def expect_hidden(self, selector: str, timeout: Optional[int] = None) -> None:
        """Assert an element is hidden."""
        timeout = timeout or self._default_timeout
        expect(self.page.locator(selector)).to_be_hidden(timeout=timeout)

    def expect_enabled(self, selector: str, timeout: Optional[int] = None) -> None:
        """Assert an element is enabled."""
        timeout = timeout or self._default_timeout
        expect(self.page.locator(selector)).to_be_enabled(timeout=timeout)

    def expect_disabled(self, selector: str, timeout: Optional[int] = None) -> None:
        """Assert an element is disabled."""
        timeout = timeout or self._default_timeout
        expect(self.page.locator(selector)).to_be_disabled(timeout=timeout)

    def expect_text(
        self, selector: str, expected_text: str, timeout: Optional[int] = None
    ) -> None:
        """Assert an element has the expected text."""
        timeout = timeout or self._default_timeout
        expect(self.page.locator(selector)).to_have_text(expected_text, timeout=timeout)

    def expect_count(
        self, selector: str, count: int, timeout: Optional[int] = None
    ) -> None:
        """Assert the number of elements matching the selector."""
        timeout = timeout or self._default_timeout
        expect(self.page.locator(selector)).to_have_count(count, timeout=timeout)

    def expect_attribute(
        self, selector: str, name: str, value: str, timeout: Optional[int] = None
    ) -> None:
        """Assert an element has the expected attribute value."""
        timeout = timeout or self._default_timeout
        expect(self.page.locator(selector)).to_have_attribute(name, value, timeout=timeout)

    def expect_url(self, pattern: str, timeout: Optional[int] = None) -> None:
        """Assert the current URL matches the pattern."""
        timeout = timeout or self._default_timeout
        expect(self.page).to_have_url(pattern, timeout=timeout)

    def expect_title(self, pattern: str, timeout: Optional[int] = None) -> None:
        """Assert the page title matches the pattern."""
        timeout = timeout or self._default_timeout
        expect(self.page).to_have_title(pattern, timeout=timeout)

    def reload(
        self,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: Optional[int] = None,
    ) -> None:
        """Reload the current page."""
        timeout = timeout or self._default_timeout
        self.page.reload(wait_until=wait_until, timeout=timeout)

    def go_back(
        self,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: Optional[int] = None,
    ) -> None:
        """Navigate back in browser history."""
        timeout = timeout or self._default_timeout
        self.page.go_back(wait_until=wait_until, timeout=timeout)

    def go_forward(
        self,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: Optional[int] = None,
    ) -> None:
        """Navigate forward in browser history."""
        timeout = timeout or self._default_timeout
        self.page.go_forward(wait_until=wait_until, timeout=timeout)

    def screenshot(self, path: Optional[str] = None, full_page: bool = True) -> Any:
        """Take a screenshot of the current page."""
        return self.page.screenshot(path=path, full_page=full_page)

    def get_count(self, selector: str, timeout: Optional[int] = None) -> int:
        """Return the count of elements matching the selector."""
        try:
            locator = self.page.locator(selector)
            if timeout:
                locator.wait_for(state="attached", timeout=timeout)
            return locator.count()
        except PlaywrightTimeoutError:
            return 0

    def wait_for_element(
        self,
        selector: str,
        state: Literal["attached", "detached", "hidden", "visible"] = "visible",
        timeout: Optional[int] = None,
    ) -> None:
        """Wait for an element to reach a specific state."""
        self.wait_for_selector(selector, state=state, timeout=timeout)

    def wait_for_elements(
        self, selector: str, min_count: int = 1, timeout: Optional[int] = None
    ):
        """Wait for at least min_count elements to be present."""
        timeout = timeout or self._default_timeout
        self.page.wait_for_function(
            f"document.querySelectorAll('{selector}').length >= {min_count}",
            timeout=timeout,
        )

    def scroll_into_view(self, selector: str, timeout: Optional[int] = None):
        """Scroll an element into view."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).scroll_into_view_if_needed(timeout=timeout)

    def get_value(self, selector: str, timeout: Optional[int] = None) -> str:
        """Get the value of an input element."""
        try:
            return (
                self.page.locator(selector).input_value(
                    timeout=timeout or self._default_timeout
                )
                or ""
            )
        except PlaywrightTimeoutError:
            return ""

    def clear(self, selector: str, timeout: Optional[int] = None):
        """Clear an input field."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).clear(timeout=timeout)

    def double_click(self, selector: str, timeout: Optional[int] = None):
        """Double click an element."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).dblclick(timeout=timeout)

    def right_click(self, selector: str, timeout: Optional[int] = None):
        """Right click an element."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).click(button="right", timeout=timeout)

    def drag_and_drop(
        self, source_selector: str, target_selector: str, timeout: Optional[int] = None
    ):
        """Drag and drop from source to target."""
        timeout = timeout or self._default_timeout
        self.page.locator(source_selector).drag_to(
            self.page.locator(target_selector), timeout=timeout
        )

    def wait_for_function(self, function: str, timeout: Optional[int] = None) -> None:
        """Wait for a JavaScript function to return truthy value."""
        timeout = timeout or self._default_timeout
        self.page.wait_for_function(function, timeout=timeout)

    def evaluate(self, expression: str, *args) -> Any:
        """Evaluate a JavaScript expression in the page context."""
        return self.page.evaluate(expression, *args)

    def evaluate_handle(self, expression: str, *args) -> Any:
        """Evaluate a JavaScript expression and return a JSHandle."""
        return self.page.evaluate_handle(expression, *args)

    # wait_for_response and wait_for_request are not available on Page in current Playwright version
    # They are available on page.context.request or page.context
    def wait_for_response(self, url_pattern: str, timeout: Optional[int] = None) -> Any:
        """Wait for a network response matching the URL pattern."""
        timeout = timeout or self._default_timeout
        # Use context to wait for response
        return self.page.context.wait_for_event("response", timeout=timeout)

    def wait_for_request(self, url_pattern: str, timeout: Optional[int] = None) -> Any:
        """Wait for a network request matching the URL pattern."""
        timeout = timeout or self._default_timeout
        # Use context to wait for request
        return self.page.context.wait_for_event("request", timeout=timeout)

    def get_cookies(self) -> List[dict]:
        """Get all cookies for the current context."""
        cookies = self.page.context.cookies()
        return [
            {
                "name": c.get("name", ""),
                "value": c.get("value", ""),
                "domain": c.get("domain", ""),
                "path": c.get("path", ""),
            }
            for c in cookies
        ]

    def set_cookie(self, cookie: Dict[str, str]) -> None:
        """Set a cookie in the current context."""
        self.page.context.add_cookies([cookie])  # type: ignore[list-item]

    def clear_cookies(self):
        """Clear all cookies in the current context."""
        self.page.context.clear_cookies()

    def get_local_storage(self) -> Dict[str, str]:
        """Get all localStorage items."""
        result = self.page.evaluate("() => JSON.parse(JSON.stringify(localStorage))")
        return result if isinstance(result, dict) else {}

    def set_local_storage(self, key: str, value: str) -> None:
        """Set a localStorage item."""
        self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")

    def clear_local_storage(self) -> None:
        """Clear all localStorage items."""
        self.page.evaluate("localStorage.clear()")

    def get_session_storage(self) -> Dict[str, str]:
        """Get all sessionStorage items."""
        result = self.page.evaluate("() => JSON.parse(JSON.stringify(sessionStorage))")
        return result if isinstance(result, dict) else {}

    def set_session_storage(self, key: str, value: str) -> None:
        """Set a sessionStorage item."""
        self.page.evaluate(f"sessionStorage.setItem('{key}', '{value}')")

    def clear_session_storage(self) -> None:
        """Clear all sessionStorage items."""
        self.page.evaluate("sessionStorage.clear()")

    def wait_for_animation(self, timeout: Optional[int] = None) -> None:
        """Wait for all CSS animations to complete."""
        timeout = timeout or self._default_timeout
        self.page.wait_for_function(
            "() => !document.querySelectorAll('*').length || "
            "Array.from(document.querySelectorAll('*')).every(el => "
            "getComputedStyle(el).animationPlayState === 'paused' || "
            "getComputedStyle(el).transitionDuration === '0s')",
            timeout=timeout,
        )

    def focus(self, selector: str, timeout: Optional[int] = None) -> None:
        """Focus an element."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).focus(timeout=timeout)

    def blur(self, selector: str, timeout: Optional[int] = None) -> None:
        """Blur an element."""
        timeout = timeout or self._default_timeout
        self.page.locator(selector).blur(timeout=timeout)

    def type_text(
        self, selector: str, text: str, delay: int = 0, timeout: Optional[int] = None
    ) -> None:
        """Type text into an input field with optional delay between keystrokes."""
        timeout = timeout or self._default_timeout
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        locator.type(text, delay=delay, timeout=timeout)

    def press_key(self, key: str, timeout: Optional[int] = None) -> None:
        """Press a key on the page."""
        timeout = timeout or self._default_timeout
        self.page.keyboard.press(key, delay=0)

    def keyboard_type(self, text: str, delay: int = 0) -> None:
        """Type text using keyboard."""
        self.page.keyboard.type(text, delay=delay)

    def take_element_screenshot(self, selector: str, path: Optional[str] = None) -> Any:
        """Take a screenshot of a specific element."""
        return self.page.locator(selector).screenshot(path=path)

    def wait_for_stable_element(
        self, selector: str, timeout: Optional[int] = None, stable_time: int = 500
    ) -> None:
        """Wait for an element to be stable (not moving/changing) for stable_time ms."""
        timeout = timeout or self._default_timeout
        self.page.wait_for_function(
            f"""
            () => {{
                const el = document.querySelector('{selector}');
                if (!el) return false;
                const rect1 = el.getBoundingClientRect();
                return new Promise(resolve => {{
                    setTimeout(() => {{
                        const rect2 = el.getBoundingClientRect();
                        resolve(rect1.x === rect2.x && rect1.y === rect2.y &&
                                rect1.width === rect2.width && rect1.height === rect2.height);
                    }}, {stable_time});
                }});
            }}
            """,
            timeout=timeout,
        )
