"""Configuration and environment settings for the test suite."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def _get_bool_env(name: str, default: bool = False) -> bool:
    """Parse a boolean environment variable."""
    value = os.getenv(name, str(default)).lower()
    return value in ("true", "1", "yes", "on")


def _get_int_env(name: str, default: int) -> int:
    """Parse an integer environment variable."""
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _get_float_env(name: str, default: float) -> float:
    """Parse a float environment variable."""
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


BASE_URL: str = os.getenv("BASE_URL", "https://fakestoreapi.com")
UI_BASE_URL: str = os.getenv("UI_BASE_URL", "https://www.saucedemo.com")
HEADLESS: bool = _get_bool_env("HEADLESS", True)
BROWSER: str = os.getenv("BROWSER", "chromium")
TIMEOUT: int = _get_int_env("TIMEOUT", 30)
RETRIES: int = _get_int_env("RETRIES", 3)
VIEWPORT_WIDTH: int = _get_int_env("VIEWPORT_WIDTH", 1280)
VIEWPORT_HEIGHT: int = _get_int_env("VIEWPORT_HEIGHT", 720)
SLOW_MO: int = _get_int_env("SLOW_MO", 0)
API_TIMEOUT: int = _get_int_env("API_TIMEOUT", 30)
VERIFY_SSL: bool = _get_bool_env("VERIFY_SSL", True)


def get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get a configuration value from environment.

    Args:
        name: The environment variable name.
        default: Default value if not set.

    Returns:
        The environment variable value or default.
    """
    return os.getenv(name, default)


def get_all_settings() -> dict:
    """Return all configuration settings as a dictionary."""
    return {
        "BASE_URL": BASE_URL,
        "UI_BASE_URL": UI_BASE_URL,
        "HEADLESS": HEADLESS,
        "BROWSER": BROWSER,
        "TIMEOUT": TIMEOUT,
        "RETRIES": RETRIES,
        "VIEWPORT_WIDTH": VIEWPORT_WIDTH,
        "VIEWPORT_HEIGHT": VIEWPORT_HEIGHT,
        "SLOW_MO": SLOW_MO,
        "API_TIMEOUT": API_TIMEOUT,
        "VERIFY_SSL": VERIFY_SSL,
    }


def validate_settings() -> bool:
    """Validate that required settings are properly configured."""
    if not BASE_URL or not BASE_URL.startswith(("http://", "https://")):
        raise ValueError("BASE_URL must be a valid HTTP/HTTPS URL")
    if not UI_BASE_URL or not UI_BASE_URL.startswith(("http://", "https://")):
        raise ValueError("UI_BASE_URL must be a valid HTTP/HTTPS URL")
    if TIMEOUT <= 0:
        raise ValueError("TIMEOUT must be positive")
    if RETRIES < 0:
        raise ValueError("RETRIES must be non-negative")
    return True