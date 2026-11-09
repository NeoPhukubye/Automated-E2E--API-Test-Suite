"""HTTP client wrapper for API testing with retry and timeout logic."""

from typing import Any, Optional
import requests
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry
from config.settings import BASE_URL, API_TIMEOUT, RETRIES, VERIFY_SSL


class APIClientError(Exception):
    """Base exception for API client errors."""


class APIClientRequestError(APIClientError):
    """Raised when a request fails after all retries."""


class APIClient:
    """Base HTTP client wrapping requests for the FakeStore API.

    Provides automatic retries (configurable attempts with exponential backoff for
    403/429/5xx), configurable timeouts, SSL verification, and session management.
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: int = API_TIMEOUT,
        retries: int = RETRIES,
        verify_ssl: bool = VERIFY_SSL,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        })
        self.session.verify = verify_ssl

        retry_strategy = Retry(
            total=retries,
            backoff_factor=2,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"],
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, endpoint: str, **kwargs: Any) -> Response:
        """Perform a GET request to the given endpoint."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)

    def post(
        self, endpoint: str, json: Optional[dict] = None, **kwargs: Any
    ) -> Response:
        """Perform a POST request to the given endpoint."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.post(
            f"{self.base_url}{endpoint}", json=json, **kwargs
        )

    def put(
        self, endpoint: str, json: Optional[dict] = None, **kwargs: Any
    ) -> Response:
        """Perform a PUT request to the given endpoint."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.put(
            f"{self.base_url}{endpoint}", json=json, **kwargs
        )

    def patch(
        self, endpoint: str, json: Optional[dict] = None, **kwargs: Any
    ) -> Response:
        """Perform a PATCH request to the given endpoint."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.patch(
            f"{self.base_url}{endpoint}", json=json, **kwargs
        )

    def delete(self, endpoint: str, **kwargs: Any) -> Response:
        """Perform a DELETE request to the given endpoint."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)

    def get_full_url(self, endpoint: str) -> str:
        """Return the full URL for an endpoint."""
        return f"{self.base_url}{endpoint}"

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()