# Automated E2E & API Test Suite

Comprehensive end-to-end and API automated test framework targeting the [FakeStore API](https://fakestoreapi.com).

## Tech Stack

- **Language:** Python 3.11+
- **Test Framework:** Pytest
- **API Testing:** Requests
- **E2E Testing:** Playwright
- **CI/CD:** GitHub Actions
- **Reporting:** Allure, pytest-html

## Project Structure

```
├── config/             # Configuration and settings
├── tests/
│   ├── api/            # API test cases
│   └── e2e/            # End-to-end UI tests
├── utils/              # Shared utilities (API client, helpers)
├── pages/              # Page Object Models for E2E tests
├── .github/workflows/  # CI pipeline
├── pytest.ini          # Pytest configuration
└── requirements.txt    # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium
cp .env.example .env
```

## Running Tests

```bash
# All tests
pytest

# API tests only
pytest -m api

# E2E tests only
pytest -m e2e

# Smoke tests
pytest -m smoke
```

## Target Application

- **API:** https://fakestoreapi.com (Products, Carts, Users, Auth)
- **UI:** FakeStore demo frontend
