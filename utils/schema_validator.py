"""JSON Schema validation contracts for API responses using Pydantic models."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic.alias_generators import to_camel


class Rating(BaseModel):
    """Product rating model."""
    rate: float = Field(ge=0, le=5)
    count: int = Field(ge=0)


class Product(BaseModel):
    """Product response model matching FakeStore API."""
    id: int
    title: str = Field(min_length=1)
    price: float = Field(ge=0)
    description: str
    category: str = Field(min_length=1)
    image: str = Field(pattern=r"^https?://")
    rating: Optional[Rating] = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class CartProduct(BaseModel):
    """Product within a cart."""
    product_id: int
    quantity: int = Field(ge=1)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class Cart(BaseModel):
    """Cart response model."""
    id: int
    user_id: int
    date: str
    products: List[CartProduct]
    v: Optional[int] = Field(default=None, alias="__v")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class Geolocation(BaseModel):
    """Geolocation coordinates."""
    lat: str
    long: str


class Address(BaseModel):
    """User address model."""
    city: str
    street: str
    number: int | float
    zipcode: str
    geolocation: Geolocation


class Name(BaseModel):
    """User name model."""
    firstname: str = Field(min_length=1)
    lastname: str = Field(min_length=1)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class User(BaseModel):
    """User response model."""
    id: int
    email: str
    username: str = Field(min_length=1)
    password: str
    name: Name
    address: Address
    phone: str
    v: Optional[int] = Field(default=None, alias="__v")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class AuthToken(BaseModel):
    """Auth token response model."""
    token: str = Field(min_length=1)


class LoginResponse(BaseModel):
    """Login response model."""
    id: int
    username: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
    firstname: str = Field(min_length=1)
    lastname: str = Field(min_length=1)
    gender: Optional[str] = None
    image: Optional[str] = None
    token: str = Field(min_length=1)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class Category(BaseModel):
    """Category response model."""
    name: str = Field(min_length=1)


# Schema dictionaries for backward compatibility with jsonschema
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

LOGIN_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["id", "username", "email", "firstName", "lastName"],
    "properties": {
        "id": {"type": "number"},
        "username": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "firstName": {"type": "string", "minLength": 1},
        "lastName": {"type": "string", "minLength": 1},
        "gender": {"type": "string"},
        "image": {"type": "string", "format": "uri"},
        "token": {"type": "string", "minLength": 1},
    },
    "additionalProperties": False,
}


def validate_product_schema(product: dict) -> Product:
    """Validate a product response against the Pydantic model.

    Args:
        product: Product dictionary to validate.

    Returns:
        Validated Product model instance.

    Raises:
        ValidationError: If validation fails.
    """
    return Product.model_validate(product)


def validate_cart_schema(cart: dict) -> Cart:
    """Validate a cart response against the Pydantic model."""
    return Cart.model_validate(cart)


def validate_user_schema(user: dict) -> User:
    """Validate a user response against the Pydantic model."""
    return User.model_validate(user)


def validate_auth_token_schema(response: dict) -> AuthToken:
    """Validate an auth token response against the Pydantic model."""
    return AuthToken.model_validate(response)


def validate_login_response_schema(response: dict) -> LoginResponse:
    """Validate a login response against the Pydantic model."""
    return LoginResponse.model_validate(response)


def validate_products(products: List[dict]) -> List[Product]:
    """Validate a list of product responses against the schema."""
    if not isinstance(products, list):
        raise TypeError(f"Expected list, got {type(products).__name__}")
    return [validate_product_schema(p) for p in products]


def validate_carts(carts: List[dict]) -> List[Cart]:
    """Validate a list of cart responses against the schema."""
    if not isinstance(carts, list):
        raise TypeError(f"Expected list, got {type(carts).__name__}")
    return [validate_cart_schema(c) for c in carts]


def validate_users(users: List[dict]) -> List[User]:
    """Validate a list of user responses against the schema."""
    if not isinstance(users, list):
        raise TypeError(f"Expected list, got {type(users).__name__}")
    return [validate_user_schema(u) for u in users]


def get_schema_for_type(entity_type: str) -> Optional[Dict[str, Any]]:
    """Return the JSON schema for a given entity type.

    Args:
        entity_type: One of 'product', 'cart', 'user', 'auth_token', 'login_response'.

    Returns:
        The JSON schema dict, or None if the type is unknown.
    """
    schemas = {
        "product": PRODUCT_SCHEMA,
        "cart": CART_SCHEMA,
        "user": USER_SCHEMA,
        "auth_token": AUTH_TOKEN_SCHEMA,
        "login_response": LOGIN_RESPONSE_SCHEMA,
    }
    return schemas.get(entity_type)


def get_model_for_type(entity_type: str) -> Optional[type]:
    """Return the Pydantic model for a given entity type.

    Args:
        entity_type: One of 'product', 'cart', 'user', 'auth_token', 'login_response'.

    Returns:
        The Pydantic model class, or None if the type is unknown.
    """
    models = {
        "product": Product,
        "cart": Cart,
        "user": User,
        "auth_token": AuthToken,
        "login_response": LoginResponse,
    }
    return models.get(entity_type)