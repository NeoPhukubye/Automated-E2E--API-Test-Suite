# Agent Configuration for Automated-E2E--API-Test-Suite

## Project Overview
Comprehensive end-to-end and API automated test framework targeting the FakeStore API and Sauce Demo web application.

## Tech Stack
- **Language**: Python 3.10+
- **Test Framework**: Pytest
- **API Testing**: Requests + JSON Schema validation
- **E2E Testing**: Playwright (Chromium)
- **CI/CD**: GitHub Actions
- **Reporting**: Allure + pytest-html
- **Coverage**: pytest-cov
- **Data Generation**: Faker
- **Linting**: Ruff
- **Type Checking**: MyPy
- **Security**: pip-audit

## Project Structure
```
├── config/                  # Configuration and environment settings
│   └── settings.py          # Pydantic-based settings from .env
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
│   │   ├── test_auth.py
│   │   ├── test_products.py
│   │   ├── test_carts.py
│   │   ├── test_users.py
│   │   ├── test_pagination.py
│   │   ├── test_negative.py
│   │   ├── test_performance.py
│   │   ├── test_integration.py
│   │   ├── test_data_consistency.py
│   │   └── test_response_metadata.py
│   └── e2e/                 # End-to-end UI tests (48 tests)
│       ├── conftest.py
│       ├── test_login.py
│       ├── test_cart_flow.py
│       ├── test_checkout_validation.py
│       ├── test_navigation.py
│       ├── test_product_browsing.py
│       ├── test_responsive.py
│       └── test_sorting_and_filters.py
├── utils/                   # Shared utilities
│   ├── api_client.py        # HTTP client with retry & timeout logic
│   ├── schema_validator.py  # JSON Schema contracts for API responses
│   └── test_data.py         # Faker-based randomized test data generator
├── .github/workflows/ci.yml # CI pipeline definition
├── pytest.ini               # Pytest configuration & custom markers
├── requirements.txt         # Python dependencies
├── Makefile                 # Common development tasks
├── .pre-commit-config.yaml  # Pre-commit hooks
└── .env.example             # Environment variable template
```

## Commands

### Installation
```bash
make install
# Or manually:
pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

### Running Tests
```bash
# All tests
make test

# API tests only (no browser required)
make test-api

# E2E tests only (requires Playwright)
make test-e2e

# By marker
make test-smoke       # Quick sanity checks
make test-regression  # Full regression suite
make test-integration # Cross-endpoint workflows
make test-performance # Response time and load tests

# Parallel execution
make test-parallel
```

### Code Quality
```bash
# Linting
make lint

# Formatting (check)
make format

# Formatting (fix)
make format-fix

# Type checking
make typecheck

# Security audit
make security

# All quality checks
make check
```

### Coverage & Reporting
```bash
# Coverage report
make coverage

# Allure report
make allure

# HTML report
pytest --html=reports/report.html --self-contained-html
```

### Pre-commit
```bash
# Install hooks
make pre-commit-install

# Run on all files
make pre-commit-run
```

### Cleanup
```bash
make clean
```

## Environment Variables
See `.env.example` for all available options:
- `BASE_URL`: FakeStore API base URL
- `UI_BASE_URL`: Sauce Demo base URL
- `HEADLESS`: Run browser in headless mode
- `BROWSER`: Browser to use (chromium, firefox, webkit)
- `TIMEOUT`: Default timeout in seconds
- `RETRIES`: Number of retry attempts
- `VIEWPORT_WIDTH/HEIGHT`: Browser viewport
- `SLOW_MO`: Slow down Playwright operations
- `API_TIMEOUT`: API request timeout
- `VERIFY_SSL`: Verify SSL certificates
- `MOCK_API`: Enable API mocking for CI

## Test Markers
| Marker | Description |
|--------|-------------|
| `@pytest.mark.api` | API-level tests (no browser) |
| `@pytest.mark.e2e` | End-to-end UI tests |
| `@pytest.mark.smoke` | Quick sanity checks for CI gating |
| `@pytest.mark.regression` | Full regression suite |
| `@pytest.mark.integration` | Workflows spanning multiple endpoints |
| `@pytest.mark.performance` | Response time and load tests |
| `@pytest.mark.external` | Tests requiring network access |
| `@pytest.mark.slow` | Slow running tests (>5s) |
| `@pytest.mark.serial` | Tests that must run serially |

## Key Patterns

### API Testing
- Use `api` fixture for APIClient with response storing for Allure
- Use `api_client` fixture for raw APIClient access
- Use `fake` or `fake_per_test` for test data generation
- Schema validation via `utils/schema_validator.py` Pydantic models

### E2E Testing
- Page Object Model: Each page has a dedicated class
- Use `logged_in_page` fixture for authenticated tests
- Use `page_with_item` / `page_with_multiple_items` for cart state
- Automatic screenshot capture on failure via conftest hook

### Adding New Tests
1. Create test file in appropriate `tests/api/` or `tests/e2e/` directory
2. Use appropriate markers (`@pytest.mark.api` or `@pytest.mark.e2e`)
3. Add Allure annotations (`@allure.feature`, `@allure.story`, `@allure.severity`)
4. Follow existing patterns for fixtures and assertions

## CI Pipeline
GitHub Actions workflow (`.github/workflows/ci.yml`) runs:
1. **lint-and-typecheck**: Ruff + MyPy across Python 3.10-3.12
2. **api-tests**: API tests across Python 3.10, 3.11, 3.12
3. **e2e-tests**: E2E tests with Playwright Chromium
4. **coverage**: Coverage reports (HTML + XML)

All jobs upload artifacts with 7-day retention.