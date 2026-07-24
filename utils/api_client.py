import requests
from config.settings import BASE_URL


class APIClient:
    """Base HTTP client wrapping requests for the FakeStore API."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def get(self, endpoint: str, **kwargs):
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)

    def post(self, endpoint: str, json=None, **kwargs):
        return self.session.post(f"{self.base_url}{endpoint}", json=json, **kwargs)

    def put(self, endpoint: str, json=None, **kwargs):
        return self.session.put(f"{self.base_url}{endpoint}", json=json, **kwargs)

    def patch(self, endpoint: str, json=None, **kwargs):
        return self.session.patch(f"{self.base_url}{endpoint}", json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)
