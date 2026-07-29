# Automated E2E & API Test Suite

Comprehensive end-to-end and API automated test framework targeting the [FakeStore API](https://fakestoreapi.com) and [Sauce Demo](https://www.saucedemo.com) web application.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Test Framework | Pytest |
| API Testing | Requests + JSON Schema validation |
| E2E Testing | Playwright (Chromium) |
| CI/CD | GitHub Actions |
| Reporting | Allure + pytest-html |
| Coverage | pytest-cov |
| Data Generation | Faker |

## Project Structure

```
├── config/                  # Configuration and environment settings
│   └── settings.py          # Loads BASE_URL, UI_BASE_URL, HEADLESS from .env
├── pages/                   # Page Object Models for E2E tests
│   ├── base_page.py         # Shared browser interaction methods
│   ├── login_page.py        # Sauce Demo login page
│   ├── home_page.py         # Inventory/product listing page
│   ├── product_page.py      # Product detail page
│   ├── cart_page.py         # Shopping cart page
│   └── checkout_page.py     # Checkout flow pages
├── tests/
│   ├── conftest.py          # Root fixtures (API client, Playwright config, Allure hooks)
│   ├── api/                 # API test cases (113 tests)
│   │   ├── test_auth.py     # Authentication & token validation
│   │   ├── test_products.py # CRUD operations on products
│   │   ├── test_carts.py    # Cart endpoint testing
│   │   ├── test_users.py    # User endpoint testing
│   │   ├── test_pagination.py       # Limit/sort query parameters
│   │   ├── test_negative.py         # Error handling & edge cases
│   │   ├── test_performance.py      # Response time assertions
│   │   ├── test_integration.py      # Cross-endpoint workflow tests
│   │   ├── test_data_consistency.py # Data integrity validation
│   │   └── test_response_metadata.py # Headers & response format
│   └── e2e/                 # End-to-end UI tests (48 tests)
│       ├── conftest.py      # E2E fixtures (login, page objects, screenshot on failure)
│       ├── test_login.py    # Login flow & error handling
│       ├── test_cart_flow.py         # Add/remove items, cart persistence
│       ├── test_checkout_validation.py # Form validation & checkout flow
│       ├── test_navigation.py        # Page navigation & auth guards
│       ├── test_product_browsing.py  # Product detail & inventory display
│       ├── test_responsive.py        # Viewport-based layout testing
│       └── test_sorting_and_filters.py # Sort order & price display
├── utils/                   # Shared utilities
│   ├── api_client.py        # HTTP client with retry & timeout logic
│   ├── schema_validator.py  # JSON Schema contracts for API responses
│   └── test_data.py         # Faker-based randomized test data generator
├── .github/workflows/ci.yml # CI pipeline definition
├── pytest.ini               # Pytest configuration & custom markers
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variable template
```

## Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/Automated-E2E--API-Test-Suite.git
cd Automated-E2E--API-Test-Suite

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install --with-deps chromium

# Configure environment
cp .env.example .env
```

## Running Tests

### Full Suite

```bash
pytest
```

### By Marker

```bash
# API tests only (no browser required)
pytest -m api

# E2E tests only (requires Playwright)
pytest -m e2e

# Smoke tests (quick sanity checks)
pytest -m smoke

# Integration tests (cross-endpoint workflows)
pytest -m integration

# Performance tests
pytest -m performance

# Regression suite
pytest -m regression
```

### By Directory

```bash
# API tests
pytest tests/api/

# E2E tests
pytest tests/e2e/

# Specific test file
pytest tests/api/test_auth.py
```

### Parallel Execution

```bash
pytest -n auto  # Uses all available CPU cores
pytest -n 4     # Uses 4 workers
```

## Test Coverage

```bash
# Run with coverage report
pytest --cov=utils --cov=pages --cov=config --cov-report=term-missing --cov-report=html:reports/coverage-html

# Open HTML report
open reports/coverage-html/index.html  # macOS
xdg-open reports/coverage-html/index.html  # Linux
```

## Reporting

### Allure Reports

```bash
# Generate Allure results
pytest --alluredir=allure-results

# Serve the report
allure serve allure-results
```

### HTML Report

```bash
pytest --html=reports/report.html --self-contained-html
```

## Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.api` | API-level tests (no browser) |
| `@pytest.mark.e2e` | End-to-end UI tests |
| `@pytest.mark.smoke` | Quick sanity checks for CI gating |
| `@pytest.mark.regression` | Full regression suite |
| `@pytest.mark.integration` | Workflows spanning multiple endpoints |
| `@pytest.mark.performance` | Response time and load tests |

## Architecture

### API Testing Layer
- **APIClient** (`utils/api_client.py`): Centralized HTTP client with automatic retries (3 attempts with exponential backoff for 429/5xx), configurable timeouts, and session management.
- **Schema Validation** (`utils/schema_validator.py`): JSON Schema contracts enforcing response structure for products, carts, users, and auth tokens.
- **Data Generation** (`utils/test_data.py`): Faker-powered random data for test isolation.

### E2E Testing Layer
- **Page Object Model**: Each page has a dedicated class encapsulating selectors and interactions, reducing test brittleness and duplication.
- **Auto-login Fixture**: `logged_in_page` fixture handles authentication before tests that require it.
- **Failure Handling**: Automatic screenshot capture on test failure, attached to Allure reports.
- **Responsive Testing**: Viewport parameterization for desktop, tablet, and mobile breakpoints.

### CI/CD Pipeline
The GitHub Actions workflow runs API and E2E tests in separate parallel jobs:
- **api-tests**: Runs without Playwright overhead, includes coverage and retry logic.
- **e2e-tests**: Installs Chromium, captures screenshots on failure, uploads Allure results.

Both jobs upload test artifacts (HTML reports, coverage, Allure results, failure screenshots).

## Target Applications

| Application | URL | Usage |
|-------------|-----|-------|
| FakeStore API | https://fakestoreapi.com | API tests (Products, Carts, Users, Auth) |
| Sauce Demo | https://www.saucedemo.com | E2E browser tests |

## Test Statistics

- **Total Tests**: 161
- **API Tests**: 113
- **E2E Tests**: 48
- **Pass Rate**: 100%
