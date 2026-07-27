from pages.base_page import BasePage
from config.settings import UI_BASE_URL


class HomePage(BasePage):
    """Page object for the Sauce Demo inventory/home page."""

    URL = f"{UI_BASE_URL}/inventory.html"
    INVENTORY_ITEM = ".inventory_item"
    INVENTORY_ITEM_NAME = ".inventory_item_name"
    INVENTORY_ITEM_PRICE = ".inventory_item_price"
    ADD_TO_CART_BUTTON = "[data-test^='add-to-cart']"
    REMOVE_BUTTON = "[data-test^='remove']"
    SHOPPING_CART_BADGE = ".shopping_cart_badge"
    SHOPPING_CART_LINK = ".shopping_cart_link"
    SORT_DROPDOWN = "[data-test='product-sort-container']"
    BURGER_MENU = "#react-burger-menu-btn"
    PAGE_TITLE = ".title"

    def navigate(self, path: str = ""):
        super().navigate(self.URL)

    def get_product_count(self) -> int:
        return self.page.locator(self.INVENTORY_ITEM).count()

    def get_product_names(self) -> list[str]:
        return self.page.locator(self.INVENTORY_ITEM_NAME).all_text_contents()

    def get_product_prices(self) -> list[str]:
        return self.page.locator(self.INVENTORY_ITEM_PRICE).all_text_contents()

    def add_item_to_cart(self, index: int = 0):
        self.page.locator(self.ADD_TO_CART_BUTTON).nth(index).click()

    def remove_item_from_cart(self, index: int = 0):
        self.page.locator(self.REMOVE_BUTTON).nth(index).click()

    def get_cart_badge_count(self) -> str:
        return self.get_text(self.SHOPPING_CART_BADGE)

    def is_cart_badge_visible(self) -> bool:
        return self.is_visible(self.SHOPPING_CART_BADGE)

    def go_to_cart(self):
        self.click(self.SHOPPING_CART_LINK)

    def sort_products(self, value: str):
        self.page.locator(self.SORT_DROPDOWN).select_option(value)

    def click_product(self, index: int = 0):
        self.page.locator(self.INVENTORY_ITEM_NAME).nth(index).click()

    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)
