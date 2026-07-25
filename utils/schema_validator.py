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
