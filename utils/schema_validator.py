"""JSON Schema validation contracts for API responses."""

from typing import Any, Dict, List, Optional
from jsonschema import validate, ValidationError


PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "price", "description", "category", "image"],
    "properties": {
        "id": {"type": "number"},
        "title": {"type": "string", "minLength": 1},
        "price": {"type": "number", "minimum": 0},
        "description": {"type": "string"},
        "category": {"type": "string", "minLength": 1},
        "image": {"type": "string", "format": "uri"},
        "rating": {
            "type": "object",
            "properties": {
                "rate": {"type": "number", "minimum": 0, "maximum": 5},
                "count": {"type": "integer", "minimum": 0},
            },
        },
    },
    "additionalProperties": False,
}

CART_SCHEMA = {
    "type": "object",
    "required": ["id", "userId", "date", "products"],
    "properties": {
        "id": {"type": "number"},
        "userId": {"type": "number"},
        "date": {"type": "string"},
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["productId", "quantity"],
                "properties": {
                    "productId": {"type": "number"},
                    "quantity": {"type": "number", "minimum": 1},
                },
            },
        },
        "__v": {"type": "number"},
    },
    "additionalProperties": False,
}

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "email", "username", "password", "name", "address", "phone"],
    "properties": {
        "id": {"type": "number"},
        "email": {"type": "string"},
        "username": {"type": "string", "minLength": 1},
        "password": {"type": "string"},
        "name": {
            "type": "object",
            "required": ["firstname", "lastname"],
            "properties": {
                "firstname": {"type": "string", "minLength": 1},
                "lastname": {"type": "string", "minLength": 1},
            },
        },
        "address": {
            "type": "object",
            "required": ["city", "street", "number", "zipcode", "geolocation"],
            "properties": {
                "city": {"type": "string"},
                "street": {"type": "string"},
                "number": {"type": ["integer", "number"]},
                "zipcode": {"type": "string"},
                "geolocation": {
                    "type": "object",
                    "required": ["lat", "long"],
                    "properties": {
                        "lat": {"type": "string"},
                        "long": {"type": "string"},
                    },
                },
            },
        },
        "phone": {"type": "string"},
        "__v": {"type": "number"},
    },
    "additionalProperties": False,
}

AUTH_TOKEN_SCHEMA = {
    "type": "object",
    "required": ["token"],
    "properties": {
        "token": {"type": "string", "minLength": 1},
    },
}


def validate_product_schema(product: dict) -> None:
    """Validate a product response against the JSON Schema contract."""
    validate(instance=product, schema=PRODUCT_SCHEMA)


def validate_cart_schema(cart: dict) -> None:
    """Validate a cart response against the JSON Schema contract."""
    validate(instance=cart, schema=CART_SCHEMA)


def validate_user_schema(user: dict) -> None:
    """Validate a user response against the JSON Schema contract."""
    validate(instance=user, schema=USER_SCHEMA)


def validate_auth_token_schema(response: dict) -> None:
    """Validate an auth token response against the JSON Schema contract."""
    validate(instance=response, schema=AUTH_TOKEN_SCHEMA)


def validate_products(products: List[dict]) -> None:
    """Validate a list of product responses against the schema."""
    if not isinstance(products, list):
        raise TypeError(f"Expected list, got {type(products).__name__}")
    for i, product in enumerate(products):
        try:
            validate_product_schema(product)
        except ValidationError as e:
            raise ValidationError(
                f"Product at index {i} failed validation: {e.message}"
            ) from e


def validate_carts(carts: List[dict]) -> None:
    """Validate a list of cart responses against the schema."""
    if not isinstance(carts, list):
        raise TypeError(f"Expected list, got {type(carts).__name__}")
    for i, cart in enumerate(carts):
        try:
            validate_cart_schema(cart)
        except ValidationError as e:
            raise ValidationError(
                f"Cart at index {i} failed validation: {e.message}"
            ) from e


def validate_users(users: List[dict]) -> None:
    """Validate a list of user responses against the schema."""
    if not isinstance(users, list):
        raise TypeError(f"Expected list, got {type(users).__name__}")
    for i, user in enumerate(users):
        try:
            validate_user_schema(user)
        except ValidationError as e:
            raise ValidationError(
                f"User at index {i} failed validation: {e.message}"
            ) from e


def get_schema_for_type(entity_type: str) -> Optional[Dict[str, Any]]:
    """Return the JSON schema for a given entity type.

    Args:
        entity_type: One of 'product', 'cart', 'user', 'auth_token'.

    Returns:
        The JSON schema dict, or None if the type is unknown.
    """
    schemas = {
        "product": PRODUCT_SCHEMA,
        "cart": CART_SCHEMA,
        "user": USER_SCHEMA,
        "auth_token": AUTH_TOKEN_SCHEMA,
    }
    return schemas.get(entity_type)