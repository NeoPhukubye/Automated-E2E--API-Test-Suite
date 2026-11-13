.PHONY: help install test test-api test-e2e test-smoke test-regression test-integration test-performance lint format typecheck coverage security clean pre-commit-install pre-commit-run allure

# Default target
help:
	@echo "Available targets:"
	@echo "  install           - Install dependencies and Playwright browsers"
	@echo "  test              - Run all tests (API + E2E)"
	@echo "  test-api          - Run API tests only"
	@echo "  test-e2e          - Run E2E tests only"
	@echo "  test-smoke        - Run smoke tests"
	@echo "  test-regression   - Run regression suite"
	@echo "  test-integration  - Run integration tests"
	@echo "  test-performance  - Run performance tests"
	@echo "  lint              - Run ruff linting"
	@echo "  format            - Run ruff formatting"
	@echo "  typecheck         - Run mypy type checking"
	@echo "  coverage          - Run tests with coverage report"
	@echo "  security          - Run pip-audit security scan"
	@echo "  clean             - Clean up generated files"
	@echo "  pre-commit-install - Install pre-commit hooks"
	@echo "  pre-commit-run    - Run pre-commit hooks on all files"
	@echo "  allure            - Generate and serve Allure report"

# Install dependencies
install:
	pip install -r requirements.txt
	python -m playwright install --with-deps chromium

# Run all tests
test:
	pytest -v --tb=short --durations=10

# Run API tests only
test-api:
	pytest tests/api/ -v --tb=short --durations=10 -m "api"

# Run E2E tests only
test-e2e:
	pytest tests/e2e/ -v --tb=short --durations=10 -m "e2e"

# Run smoke tests
test-smoke:
	pytest -m "smoke" -v --tb=short

# Run regression suite
test-regression:
	pytest -m "regression" -v --tb=short --durations=10

# Run integration tests
test-integration:
	pytest -m "integration" -v --tb=short --durations=10

# Run performance tests
test-performance:
	pytest -m "performance" -v --tb=short --durations=10

# Run linting
lint:
	ruff check .

# Run formatting check
format:
	ruff format --check .

# Run formatting (fix)
format-fix:
	ruff format .

# Run type checking
typecheck:
	mypy --strict .

# Run tests with coverage
coverage:
	pytest --cov=utils --cov=pages --cov=config \
		--cov-report=term-missing \
		--cov-report=html:reports/coverage-html \
		--cov-report=xml:reports/coverage.xml

# Run security audit
security:
	pip-audit --desc

# Clean up generated files
clean:
	rm -rf __pycache__ .pytest_cache .coverage reports/coverage-html reports/coverage.xml
	rm -rf allure-results reports/*.html reports/*.xml reports/screenshots/*.png
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Install pre-commit hooks
pre-commit-install:
	pre-commit install

# Run pre-commit hooks on all files
pre-commit-run:
	pre-commit run --all-files

# Generate and serve Allure report
allure:
	pytest --alluredir=allure-results
	allure serve allure-results

# Run all quality checks
check: lint format typecheck security

# Run all tests with coverage and quality checks
ci: check test coverage

# Parallel test execution
test-parallel:
	pytest -n auto -v --tb=short --durations=10