from pages.base_page import BasePage


class ProductPage(BasePage):
    """Page object for the Sauce Demo product detail page."""

    PRODUCT_NAME = "[data-test='inventory-item-name']"
    PRODUCT_DESCRIPTION = "[data-test='inventory-item-desc']"
    PRODUCT_PRICE = "[data-test='inventory-item-price']"
    ADD_TO_CART_BUTTON = "[data-test^='add-to-cart']"
    REMOVE_BUTTON = "[data-test^='remove']"
    BACK_BUTTON = "#back-to-products"

    def get_product_name(self) -> str:
        return self.get_text(self.PRODUCT_NAME)

    def get_product_description(self) -> str:
        return self.get_text(self.PRODUCT_DESCRIPTION)

    def get_product_price(self) -> str:
        return self.get_text(self.PRODUCT_PRICE)

    def add_to_cart(self):
        self.click(self.ADD_TO_CART_BUTTON)

    def remove_from_cart(self):
        self.click(self.REMOVE_BUTTON)

    def go_back(self):
        self.click(self.BACK_BUTTON)
