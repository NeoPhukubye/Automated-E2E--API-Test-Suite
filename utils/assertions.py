"""Common assertion helpers for tests."""

import allure
from typing import Any, List, Optional, Union
from jsonschema import ValidationError
from requests.models import Response


def assert_status_code(
    response: Response, expected: int, message: str = "", accepted_codes: Optional[List[int]] = None
) -> None:
    """Assert response status code with detailed failure message."""
    actual = response.status_code
    valid_codes = [expected] + (accepted_codes or [])
    msg = message or f"Expected status {valid_codes}, got {actual}"
    if actual not in valid_codes:
        try:
            body = response.json()
        except Exception:
            body = response.text
        allure.attach(
            str(body), name="Response Body", attachment_type=allure.attachment_type.JSON
        )
        allure.attach(
            str(actual),
            name="Actual Status",
            attachment_type=allure.attachment_type.TEXT,
        )
    assert actual in valid_codes, msg


def assert_json_response(response: Response, message: str = "") -> Any:
    """Assert response is valid JSON and return parsed data."""
    try:
        data = response.json()
    except Exception as e:
        allure.attach(
            response.text,
            name="Response Text",
            attachment_type=allure.attachment_type.TEXT,
        )
        raise AssertionError(message or f"Response is not valid JSON: {e}") from e
    return data


def assert_schema_valid(
    data: dict, schema: dict, entity_name: str = "entity", index: Optional[int] = None
) -> None:
    """Validate data against JSON schema with detailed error reporting."""
    from jsonschema import validate

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        idx_msg = f" at index {index}" if index is not None else ""
        msg = f"{entity_name}{idx_msg} validation failed: {e.message}"
        allure.attach(
            str(data),
            name=f"{entity_name} Data",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            str(e), name="Validation Error", attachment_type=allure.attachment_type.TEXT
        )
        raise AssertionError(msg) from e


def assert_list_not_empty(items: List[Any], message: str = "") -> None:
    """Assert a list is not empty."""
    msg = message or "Expected non-empty list"
    assert isinstance(items, list), f"{msg}: got {type(items).__name__}"
    assert len(items) > 0, msg


def assert_has_keys(data: dict, required_keys: List[str], message: str = ""):
    """Assert a dictionary has all required keys."""
    missing = [k for k in required_keys if k not in data]
    msg = message or f"Missing required keys: {missing}"
    assert not missing, msg


def assert_field_type(data: dict, field: str, expected_type: type, message: str = ""):
    """Assert a field exists and is of expected type."""
    assert field in data, f"Field '{field}' not in data"
    actual = data[field]
    msg = (
        message
        or f"Field '{field}' expected {expected_type.__name__}, got {type(actual).__name__}"
    )
    assert isinstance(actual, expected_type), msg


def assert_field_value(data: dict, field: str, expected: Any, message: str = ""):
    """Assert a field has a specific value."""
    assert field in data, f"Field '{field}' not in data"
    actual = data[field]
    msg = message or f"Field '{field}' expected {expected!r}, got {actual!r}"
    assert actual == expected, msg


def assert_response_time(response, max_seconds: float, message: str = ""):
    """Assert response time is within acceptable limit."""
    elapsed = response.elapsed.total_seconds()
    msg = message or f"Response time {elapsed:.3f}s exceeds limit {max_seconds}s"
    assert elapsed <= max_seconds, msg


def assert_content_type(
    response, expected: str = "application/json", message: str = ""
):
    """Assert response Content-Type header."""
    actual = response.headers.get("Content-Type", "")
    msg = message or f"Expected Content-Type '{expected}', got '{actual}'"
    assert expected in actual, msg


def assert_headers_present(response, headers: List[str], message: str = ""):
    """Assert response has all required headers."""
    missing = [h for h in headers if h not in response.headers]
    msg = message or f"Missing headers: {missing}"
    assert not missing, msg


def assert_field_exists(data: dict, field: str, message: str = ""):
    """Assert a field exists in the data."""
    msg = message or f"Field '{field}' not found in data"
    assert field in data, msg


def assert_field_not_exists(data: dict, field: str, message: str = ""):
    """Assert a field does not exist in the data."""
    msg = message or f"Field '{field}' should not exist in data"
    assert field not in data, msg


def assert_list_contains(items: list, expected_item: Any, message: str = ""):
    """Assert a list contains a specific item."""
    msg = message or f"Expected list to contain {expected_item!r}"
    assert expected_item in items, msg


def assert_list_not_contains(items: list, unexpected_item: Any, message: str = ""):
    """Assert a list does not contain a specific item."""
    msg = message or f"Expected list to not contain {unexpected_item!r}"
    assert unexpected_item not in items, msg


def assert_dict_equal(
    actual: dict, expected: dict, message: str = "", ignore_keys: Optional[List[str]] = None
) -> None:
    """Assert two dictionaries are equal, optionally ignoring keys."""
    ignore_keys = ignore_keys or []
    filtered_actual = {k: v for k, v in actual.items() if k not in ignore_keys}
    filtered_expected = {k: v for k, v in expected.items() if k not in ignore_keys}
    msg = message or f"Dicts not equal: {filtered_actual} != {filtered_expected}"
    assert filtered_actual == filtered_expected, msg


def assert_dict_subset(subset: dict, superset: dict, message: str = ""):
    """Assert all key-value pairs in subset exist in superset."""
    missing = {}
    for k, v in subset.items():
        if k not in superset:
            missing[k] = v
        elif superset[k] != v:
            missing[k] = f"expected {v!r}, got {superset[k]!r}"
    msg = message or f"Subset not found in superset: {missing}"
    assert not missing, msg


def assert_numeric_range(
    value: Union[int, float],
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    message: str = "",
) -> None:
    """Assert a numeric value is within a range."""
    if min_val is not None:
        msg = message or f"Value {value} is less than minimum {min_val}"
        assert value >= min_val, msg
    if max_val is not None:
        msg = message or f"Value {value} is greater than maximum {max_val}"
        assert value <= max_val, msg


def assert_string_matches(value: str, pattern: str, message: str = ""):
    """Assert a string matches a regex pattern."""
    import re

    msg = message or f"String '{value}' does not match pattern '{pattern}'"
    assert re.match(pattern, value), msg


def assert_string_length(
    value: str, min_len: int = 0, max_len: Optional[int] = None, message: str = ""
) -> None:
    """Assert a string length is within bounds."""
    if min_len:
        msg = message or f"String length {len(value)} is less than minimum {min_len}"
        assert len(value) >= min_len, msg
    if max_len is not None:
        msg = message or f"String length {len(value)} exceeds maximum {max_len}"
        assert len(value) <= max_len, msg


def assert_is_true(value: Any, message: str = ""):
    """Assert a value is truthy."""
    msg = message or f"Expected truthy value, got {value!r}"
    assert value, msg


def assert_is_false(value: Any, message: str = ""):
    """Assert a value is falsy."""
    msg = message or f"Expected falsy value, got {value!r}"
    assert not value, msg


def assert_is_none(value: Any, message: str = ""):
    """Assert a value is None."""
    msg = message or f"Expected None, got {value!r}"
    assert value is None, msg


def assert_is_not_none(value: Any, message: str = ""):
    """Assert a value is not None."""
    msg = message or f"Expected not None, got {value!r}"
    assert value is not None, msg


def assert_instance_of(obj: Any, expected_type: type, message: str = ""):
    """Assert an object is an instance of the expected type."""
    msg = message or f"Expected {expected_type.__name__}, got {type(obj).__name__}"
    assert isinstance(obj, expected_type), msg


def assert_greater_than(
    actual: Union[int, float], expected: Union[int, float], message: str = ""
):
    """Assert actual is greater than expected."""
    msg = message or f"Expected {actual} > {expected}"
    assert actual > expected, msg


def assert_less_than(
    actual: Union[int, float], expected: Union[int, float], message: str = ""
):
    """Assert actual is less than expected."""
    msg = message or f"Expected {actual} < {expected}"
    assert actual < expected, msg


def assert_greater_equal(
    actual: Union[int, float], expected: Union[int, float], message: str = ""
):
    """Assert actual is greater than or equal to expected."""
    msg = message or f"Expected {actual} >= {expected}"
    assert actual >= expected, msg


def assert_less_equal(
    actual: Union[int, float], expected: Union[int, float], message: str = ""
):
    """Assert actual is less than or equal to expected."""
    msg = message or f"Expected {actual} <= {expected}"
    assert actual <= expected, msg


def assert_almost_equal(
    actual: float, expected: float, places: int = 7, message: str = ""
):
    """Assert two floats are almost equal within given decimal places."""
    msg = message or f"Expected {actual} ≈ {expected} (places={places})"
    assert round(abs(actual - expected), places) == 0, msg
