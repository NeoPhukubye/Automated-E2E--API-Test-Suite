from pages.base_page import BasePage
from config.settings import TIMEOUT
from typing import Optional, Literal


class ProductPage(BasePage):
    """Page object for the Sauce Demo product detail page."""

    PRODUCT_NAME = "[data-test='inventory-item-name']"
    PRODUCT_DESCRIPTION = "[data-test='inventory-item-desc']"
    PRODUCT_PRICE = "[data-test='inventory-item-price']"
    ADD_TO_CART_BUTTON = "[data-test^='add-to-cart']"
    REMOVE_BUTTON = "[data-test^='remove']"
    BACK_BUTTON = "#back-to-products"
    PRODUCT_IMAGE = ".inventory_item_img"

    def wait_until_ready(self, timeout: int = TIMEOUT * 1000) -> None:
        """Wait for the product detail container to render."""
        self.page.locator(self.PRODUCT_NAME).first.wait_for(
            state="visible", timeout=timeout
        )

    def get_product_name(self) -> str:
        return self.get_text(self.PRODUCT_NAME)

    def get_product_description(self) -> str:
        return self.get_text(self.PRODUCT_DESCRIPTION)

    def get_product_price(self) -> str:
        return self.get_text(self.PRODUCT_PRICE)

    def get_image_src(self) -> Optional[str]:
        return self.page.locator(self.PRODUCT_IMAGE).first.get_attribute("src")

    def add_to_cart(self) -> None:
        self.click(self.ADD_TO_CART_BUTTON)

    def remove_from_cart(self) -> None:
        self.click(self.REMOVE_BUTTON)

    def go_back(
        self,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "networkidle",
        timeout: Optional[int] = None,
    ) -> None:
        self.click(self.BACK_BUTTON)
        super().go_back(wait_until=wait_until, timeout=timeout)
