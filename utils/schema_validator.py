def validate_product_schema(product: dict) -> None:
    """Assert that a product response contains all expected fields with correct types."""
    required_fields = {
        "id": (int, float),
        "title": str,
        "price": (int, float),
        "description": str,
        "category": str,
        "image": str,
    }
    for field, expected_type in required_fields.items():
        assert field in product, f"Missing field: {field}"
        assert isinstance(product[field], expected_type), (
            f"Field '{field}' expected {expected_type}, got {type(product[field])}"
        )


def validate_cart_schema(cart: dict) -> None:
    """Assert that a cart response contains all expected fields with correct types."""
    required_fields = {
        "id": (int, float),
        "userId": (int, float),
        "date": str,
        "products": list,
    }
    for field, expected_type in required_fields.items():
        assert field in cart, f"Missing field: {field}"
        assert isinstance(cart[field], expected_type), (
            f"Field '{field}' expected {expected_type}, got {type(cart[field])}"
        )
    for item in cart["products"]:
        assert "productId" in item, "Cart product missing 'productId'"
        assert "quantity" in item, "Cart product missing 'quantity'"


def validate_user_schema(user: dict) -> None:
    """Assert that a user response contains all expected fields with correct types."""
    required_fields = {
        "id": (int, float),
        "email": str,
        "username": str,
        "password": str,
        "phone": str,
    }
    for field, expected_type in required_fields.items():
        assert field in user, f"Missing field: {field}"
        assert isinstance(user[field], expected_type), (
            f"Field '{field}' expected {expected_type}, got {type(user[field])}"
        )
    assert "name" in user, "Missing field: name"
    assert "firstname" in user["name"], "Missing field: name.firstname"
    assert "lastname" in user["name"], "Missing field: name.lastname"
    assert "address" in user, "Missing field: address"
