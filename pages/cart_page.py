from pages.base_page import BasePage
from config.settings import UI_BASE_URL, TIMEOUT


class CartPage(BasePage):
    """Page object for the Sauce Demo cart page."""

    URL = f"{UI_BASE_URL}/cart.html"
    CART_ITEM = ".cart_item"
    CART_ITEM_NAME = ".inventory_item_name"
    CART_ITEM_PRICE = ".inventory_item_price"
    REMOVE_BUTTON = "[data-test^='remove']"
    CONTINUE_SHOPPING_BUTTON = "#continue-shopping"
    CHECKOUT_BUTTON = "#checkout"
    PAGE_TITLE = ".title"

    def navigate(self, path: str = ""):
        super().navigate(self.URL)
        self.wait_until_ready()

    def wait_until_ready(self, timeout: int = TIMEOUT * 1000):
        """Wait for the cart page title to render."""
        self.page.locator(self.PAGE_TITLE).first.wait_for(
            state="visible", timeout=timeout
        )

    def get_cart_item_count(self) -> int:
        self.wait_until_ready()
        return self.page.locator(self.CART_ITEM).count()

    def get_cart_item_names(self) -> list[str]:
        self.wait_until_ready()
        return self.page.locator(self.CART_ITEM_NAME).all_text_contents()

    def get_cart_item_prices(self) -> list[str]:
        self.wait_until_ready()
        return self.page.locator(self.CART_ITEM_PRICE).all_text_contents()

    def remove_item(self, index: int = 0):
        self.wait_until_ready()
        self.page.locator(self.REMOVE_BUTTON).nth(index).click()

    def continue_shopping(self):
        self.click(self.CONTINUE_SHOPPING_BUTTON)

    def proceed_to_checkout(self):
        self.wait_until_ready()
        self.click(self.CHECKOUT_BUTTON)

    def get_page_title(self) -> str:
        self.wait_until_ready()
        return self.get_text(self.PAGE_TITLE)
