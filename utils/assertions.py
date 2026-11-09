"""Common assertion helpers for tests."""

from typing import Any, Dict, List, Optional
import allure
from jsonschema import ValidationError


def assert_status_code(response, expected: int, message: str = ""):
    """Assert response status code with detailed failure message."""
    actual = response.status_code
    msg = message or f"Expected status {expected}, got {actual}"
    if actual != expected:
        try:
            body = response.json()
        except Exception:
            body = response.text
        allure.attach(str(body), name="Response Body", attachment_type=allure.attachment_type.JSON)
        allure.attach(str(actual), name="Actual Status", attachment_type=allure.attachment_type.TEXT)
    assert actual == expected, msg


def assert_json_response(response, message: str = ""):
    """Assert response is valid JSON and return parsed data."""
    try:
        data = response.json()
    except Exception as e:
        allure.attach(response.text, name="Response Text", attachment_type=allure.attachment_type.TEXT)
        raise AssertionError(message or f"Response is not valid JSON: {e}") from e
    return data


def assert_schema_valid(data: dict, schema: dict, entity_name: str = "entity", index: int = None):
    """Validate data against JSON schema with detailed error reporting."""
    from jsonschema import validate
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        idx_msg = f" at index {index}" if index is not None else ""
        msg = f"{entity_name}{idx_msg} validation failed: {e.message}"
        allure.attach(str(data), name=f"{entity_name} Data", attachment_type=allure.attachment_type.JSON)
        allure.attach(str(e), name="Validation Error", attachment_type=allure.attachment_type.TEXT)
        raise AssertionError(msg) from e


def assert_list_not_empty(items: list, message: str = ""):
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
    msg = message or f"Field '{field}' expected {expected_type.__name__}, got {type(actual).__name__}"
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


def assert_content_type(response, expected: str = "application/json", message: str = ""):
    """Assert response Content-Type header."""
    actual = response.headers.get("Content-Type", "")
    msg = message or f"Expected Content-Type '{expected}', got '{actual}'"
    assert expected in actual, msg


def assert_headers_present(response, headers: List[str], message: str = ""):
    """Assert response has all required headers."""
    missing = [h for h in headers if h not in response.headers]
    msg = message or f"Missing headers: {missing}"
    assert not missing, msg