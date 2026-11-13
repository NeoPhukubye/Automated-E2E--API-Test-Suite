"""Configuration and environment settings for the test suite using Pydantic."""

import os
from typing import Optional, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    BASE_URL: str = Field(
        default="https://fakestoreapi.com",
        description="Base URL for API tests",
    )
    UI_BASE_URL: str = Field(
        default="https://www.saucedemo.com",
        description="Base URL for E2E tests",
    )
    HEADLESS: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )
    BROWSER: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium",
        description="Browser to use for E2E tests",
    )
    TIMEOUT: int = Field(
        default=30,
        ge=1,
        description="Default timeout in seconds for E2E tests",
    )
    RETRIES: int = Field(
        default=3,
        ge=0,
        description="Number of retry attempts for failed requests",
    )
    VIEWPORT_WIDTH: int = Field(
        default=1280,
        ge=320,
        description="Browser viewport width",
    )
    VIEWPORT_HEIGHT: int = Field(
        default=720,
        ge=240,
        description="Browser viewport height",
    )
    SLOW_MO: int = Field(
        default=0,
        ge=0,
        description="Slow down Playwright operations by N ms (debugging)",
    )
    API_TIMEOUT: int = Field(
        default=30,
        ge=1,
        description="API request timeout in seconds",
    )
    VERIFY_SSL: bool = Field(
        default=True,
        description="Verify SSL certificates for API requests",
    )
    MOCK_API: bool = Field(
        default=False,
        description="Enable API mocking for CI environments",
    )

    @field_validator("BASE_URL", "UI_BASE_URL", mode="before")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v or not v.startswith(("http://", "https://")):
            raise ValueError("Must be a valid HTTP/HTTPS URL")
        return v.rstrip("/")

    @field_validator("HEADLESS", "VERIFY_SSL", "MOCK_API", mode="before")
    @classmethod
    def parse_bool(cls, v: str | bool) -> bool:
        if isinstance(v, bool):
            return v
        return v.lower() in ("true", "1", "yes", "on")

    def get_all_settings(self) -> dict:
        """Return all configuration settings as a dictionary."""
        return self.model_dump()

    def validate_settings(self) -> bool:
        """Validate that required settings are properly configured."""
        self.model_validate(self)
        return True


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get a configuration value from environment.

    Args:
        name: The environment variable name.
        default: Default value if not set.

    Returns:
        The environment variable value or default.
    """
    return os.getenv(name, default)


# For backward compatibility, expose settings as module-level constants
_settings_instance = get_settings()
BASE_URL = _settings_instance.BASE_URL
UI_BASE_URL = _settings_instance.UI_BASE_URL
HEADLESS = _settings_instance.HEADLESS
BROWSER = _settings_instance.BROWSER
TIMEOUT = _settings_instance.TIMEOUT
RETRIES = _settings_instance.RETRIES
VIEWPORT_WIDTH = _settings_instance.VIEWPORT_WIDTH
VIEWPORT_HEIGHT = _settings_instance.VIEWPORT_HEIGHT
SLOW_MO = _settings_instance.SLOW_MO
API_TIMEOUT = _settings_instance.API_TIMEOUT
VERIFY_SSL = _settings_instance.VERIFY_SSL
MOCK_API = _settings_instance.MOCK_API


def validate_settings() -> bool:
    """Validate that required settings are properly configured."""
    _settings_instance.validate_settings()
    return True
