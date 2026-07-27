from pages.base_page import BasePage
from config.settings import UI_BASE_URL


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

    def get_cart_item_count(self) -> int:
        return self.page.locator(self.CART_ITEM).count()

    def get_cart_item_names(self) -> list[str]:
        return self.page.locator(self.CART_ITEM_NAME).all_text_contents()

    def get_cart_item_prices(self) -> list[str]:
        return self.page.locator(self.CART_ITEM_PRICE).all_text_contents()

    def remove_item(self, index: int = 0):
        self.page.locator(self.REMOVE_BUTTON).nth(index).click()

    def continue_shopping(self):
        self.click(self.CONTINUE_SHOPPING_BUTTON)

    def proceed_to_checkout(self):
        self.click(self.CHECKOUT_BUTTON)

    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)
