"""HTTP client wrapper for API testing with retry, timeout logic, and logging."""

import logging
import time
from typing import Any, Optional, Dict
from dataclasses import dataclass, field

import requests
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry

from config.settings import BASE_URL, API_TIMEOUT, RETRIES, VERIFY_SSL


logger = logging.getLogger(__name__)


@dataclass
class RequestLog:
    """Data class for storing request/response details for debugging."""
    method: str
    url: str
    request_headers: Dict[str, str] = field(default_factory=dict)
    request_body: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: Optional[str] = None
    elapsed_ms: float = 0.0
    error: Optional[str] = None


class APIClientError(Exception):
    """Base exception for API client errors."""

    def __init__(self, message: str, request_log: Optional[RequestLog] = None):
        super().__init__(message)
        self.request_log = request_log


class APIClientRequestError(APIClientError):
    """Raised when a request fails after all retries."""


class APIClientResponseError(APIClientError):
    """Raised when response validation fails."""

    def __init__(
        self,
        message: str,
        response: Response,
        request_log: Optional[RequestLog] = None,
    ):
        super().__init__(message, request_log)
        self.response = response


class APIClient:
    """Base HTTP client wrapping requests for the FakeStore API.

    Provides automatic retries (configurable attempts with exponential backoff for
    403/429/5xx), configurable timeouts, SSL verification, session management,
    and detailed request/response logging for debugging.
    """

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: int = API_TIMEOUT,
        retries: int = RETRIES,
        verify_ssl: bool = VERIFY_SSL,
        log_requests: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.log_requests = log_requests
        self._last_request_log: Optional[RequestLog] = None

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

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    def _log_request(self, log: RequestLog) -> None:
        """Log request/response details."""
        if not self.log_requests:
            return

        if log.error:
            logger.error(
                "API Request Failed: %s %s - Error: %s",
                log.method, log.url, log.error
            )
        else:
            logger.info(
                "API Request: %s %s - Status: %s - Time: %.2fms",
                log.method, log.url, log.response_status, log.elapsed_ms
            )

        self._last_request_log = log

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
    ) -> Response:
        """Internal method to execute HTTP request with logging."""
        url = self._build_url(endpoint)
        start_time = time.perf_counter()

        log = RequestLog(
            method=method.upper(),
            url=url,
            request_headers=dict(self.session.headers),
            request_body=kwargs.get("json"),
        )

        try:
            kwargs.setdefault("timeout", self.timeout)
            response = self.session.request(method, url, **kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            log.response_status = response.status_code
            log.response_headers = dict(response.headers)
            log.response_body = response.text[:2000]  # Truncate large responses
            log.elapsed_ms = elapsed_ms

            self._log_request(log)
            return response

        except requests.exceptions.Timeout as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            log.error = f"Timeout after {self.timeout}s"
            log.elapsed_ms = elapsed_ms
            self._log_request(log)
            raise APIClientRequestError(
                f"Request timed out after {self.timeout}s: {url}",
                request_log=log
            ) from e

        except requests.exceptions.ConnectionError as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            log.error = f"Connection error: {e}"
            log.elapsed_ms = elapsed_ms
            self._log_request(log)
            raise APIClientRequestError(
                f"Connection error for {url}: {e}",
                request_log=log
            ) from e

        except requests.exceptions.RequestException as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            log.error = f"Request error: {e}"
            log.elapsed_ms = elapsed_ms
            self._log_request(log)
            raise APIClientRequestError(
                f"Request failed for {url}: {e}",
                request_log=log
            ) from e

    def get(self, endpoint: str, **kwargs: Any) -> Response:
        """Perform a GET request to the given endpoint."""
        return self._request("GET", endpoint, **kwargs)

    def post(
        self, endpoint: str, json: Optional[dict] = None, **kwargs: Any
    ) -> Response:
        """Perform a POST request to the given endpoint."""
        return self._request("POST", endpoint, json=json, **kwargs)

    def put(
        self, endpoint: str, json: Optional[dict] = None, **kwargs: Any
    ) -> Response:
        """Perform a PUT request to the given endpoint."""
        return self._request("PUT", endpoint, json=json, **kwargs)

    def patch(
        self, endpoint: str, json: Optional[dict] = None, **kwargs: Any
    ) -> Response:
        """Perform a PATCH request to the given endpoint."""
        return self._request("PATCH", endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Response:
        """Perform a DELETE request to the given endpoint."""
        return self._request("DELETE", endpoint, **kwargs)

    def head(self, endpoint: str, **kwargs: Any) -> Response:
        """Perform a HEAD request to the given endpoint."""
        return self._request("HEAD", endpoint, **kwargs)

    def options(self, endpoint: str, **kwargs: Any) -> Response:
        """Perform an OPTIONS request to the given endpoint."""
        return self._request("OPTIONS", endpoint, **kwargs)

    def get_full_url(self, endpoint: str) -> str:
        """Return the full URL for an endpoint."""
        return self._build_url(endpoint)

    def get_last_request_log(self) -> Optional[RequestLog]:
        """Get the last request log for debugging."""
        return self._last_request_log

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()