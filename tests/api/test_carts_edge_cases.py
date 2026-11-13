"""Tests for cart operations and edge cases."""

import pytest
import allure
from utils.assertions import (
    assert_status_code,
    assert_json_response,
    assert_list_not_empty,
)
from utils.schema_validator import validate_cart_schema


@pytest.mark.api
@allure.feature("Carts")
class TestCartsEdgeCases:
    """Additional cart tests for edge cases and validation."""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Cart Schema Validation")
    def test_get_single_cart_schema_valid(self, api):
        """Verify cart response matches JSON schema."""
        response = api.get("/carts/1")
        assert_status_code(response, 200)
        cart = assert_json_response(response)
        validate_cart_schema(cart)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Cart Date Format")
    def test_cart_date_is_iso_format(self, api):
        """Verify cart date is in ISO format."""
        response = api.get("/carts/1")
        assert_status_code(response, 200)
        cart = assert_json_response(response)
        date_str = cart["date"]
        assert "T" in date_str or "-" in date_str

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Cart Products Structure")
    def test_cart_products_have_required_fields(self, api):
        """Verify cart products have productId and quantity."""
        response = api.get("/carts/1")
        assert_status_code(response, 200)
        cart = assert_json_response(response)
        for item in cart["products"]:
            assert "productId" in item
            assert "quantity" in item
            assert isinstance(item["productId"], (int, float))
            assert isinstance(item["quantity"], (int, float))

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Cart User Isolation")
    def test_user_carts_isolated(self, api):
        """Verify user carts are isolated by userId."""
        response1 = api.get("/carts/user/1")
        response2 = api.get("/carts/user/2")
        assert_status_code(response1, 200)
        assert_status_code(response2, 200)
        carts1 = assert_json_response(response1)
        carts2 = assert_json_response(response2)
        for cart in carts1:
            assert cart["userId"] == 1
        for cart in carts2:
            assert cart["userId"] == 2

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Cart ID Type")
    def test_cart_id_is_number(self, api):
        """Verify cart id is a number."""
        response = api.get("/carts/1")
        assert_status_code(response, 200)
        cart = assert_json_response(response)
        assert isinstance(cart["id"], (int, float))

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Create Cart Validation")
    def test_create_cart_with_valid_products(self, api):
        """Verify creating a cart with valid product IDs."""
        payload = {
            "userId": 1,
            "date": "2024-01-01",
            "products": [
                {"productId": 1, "quantity": 2},
                {"productId": 2, "quantity": 1},
            ],
        }
        response = api.post("/carts", json=payload)
        assert_status_code(response, 201, accepted_codes=[200])
        cart = assert_json_response(response)
        assert "id" in cart
        assert len(cart["products"]) == 2

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Cart Update")
    def test_update_cart_preserves_id(self, api):
        """Verify updating a cart preserves its id."""
        payload = {
            "userId": 1,
            "date": "2024-01-01",
            "products": [{"productId": 1, "quantity": 5}],
        }
        response = api.put("/carts/1", json=payload)
        assert_status_code(response, 200)
        cart = assert_json_response(response)
        assert cart["id"] == 1

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("Cart Empty Products")
    def test_get_carts_structure(self, api):
        """Verify all carts have consistent structure."""
        response = api.get("/carts")
        assert_status_code(response, 200)
        carts = assert_json_response(response)
        assert_list_not_empty(carts)
        for cart in carts:
            assert "id" in cart
            assert "userId" in cart
            assert "date" in cart
            assert "products" in cart
            assert isinstance(cart["products"], list)
