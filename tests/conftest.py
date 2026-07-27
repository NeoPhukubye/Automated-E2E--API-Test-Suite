import pytest
import allure
from utils.api_client import APIClient


@pytest.fixture(scope="session")
def api():
    """Provide a shared API client instance for the test session."""
    return APIClient()


@pytest.fixture(autouse=True)
def attach_api_response(request):
    """Attach API response details to Allure report on failure."""
    yield
    if request.node.rep_call and request.node.rep_call.failed:
        if hasattr(request.node, "last_response"):
            response = request.node.last_response
            allure.attach(
                str(response.status_code),
                name="Status Code",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                response.text[:2000],
                name="Response Body",
                attachment_type=allure.attachment_type.JSON,
            )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test report on the item for fixture access."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
