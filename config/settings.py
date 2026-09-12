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


BASE_URL: str = os.getenv("BASE_URL", "https://fakestoreapi.com")
UI_BASE_URL: str = os.getenv("UI_BASE_URL", "https://www.saucedemo.com")
HEADLESS: bool = _get_bool_env("HEADLESS", True)
BROWSER: str = os.getenv("BROWSER", "chromium")
TIMEOUT: int = _get_int_env("TIMEOUT", 30)
RETRIES: int = _get_int_env("RETRIES", 3)
VIEWPORT_WIDTH: int = _get_int_env("VIEWPORT_WIDTH", 1280)
VIEWPORT_HEIGHT: int = _get_int_env("VIEWPORT_HEIGHT", 720)


def get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get a configuration value from environment.

    Args:
        name: The environment variable name.
        default: Default value if not set.

    Returns:
        The environment variable value or default.
    """
    return os.getenv(name, default)