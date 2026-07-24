import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import BASE_URL


class APIClient:
    """Base HTTP client wrapping requests for the FakeStore API."""

    def __init__(self, base_url: str = BASE_URL, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, endpoint: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)

    def post(self, endpoint: str, json=None, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.post(f"{self.base_url}{endpoint}", json=json, **kwargs)

    def put(self, endpoint: str, json=None, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.put(f"{self.base_url}{endpoint}", json=json, **kwargs)

    def patch(self, endpoint: str, json=None, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.patch(f"{self.base_url}{endpoint}", json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)
