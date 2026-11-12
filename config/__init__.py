"""Configuration package for the test suite."""

from config.settings import (
    BASE_URL,
    UI_BASE_URL,
    HEADLESS,
    BROWSER,
    TIMEOUT,
    RETRIES,
    VIEWPORT_WIDTH,
    VIEWPORT_HEIGHT,
    SLOW_MO,
    API_TIMEOUT,
    VERIFY_SSL,
    MOCK_API,
    get_setting,
    get_settings,
    validate_settings,
)

__all__ = [
    "BASE_URL",
    "UI_BASE_URL",
    "HEADLESS",
    "BROWSER",
    "TIMEOUT",
    "RETRIES",
    "VIEWPORT_WIDTH",
    "VIEWPORT_HEIGHT",
    "SLOW_MO",
    "API_TIMEOUT",
    "VERIFY_SSL",
    "MOCK_API",
    "get_setting",
    "get_settings",
    "validate_settings",
]