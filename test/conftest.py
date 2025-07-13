
import pytest

# Required for pytest to recognize --formats CLI option
def pytest_addoption(parser):
    parser.addoption(
        "--formats",
        action="store",
        default="csv,json,xlsx",
        help="Comma-separated export formats (e.g., csv,json,excel)",
    )

# Fixture that reads --formats and returns cleaned list
@pytest.fixture(scope="session")
def expected_extensions(request):
    raw = request.config.getoption("--formats")
    return [
        fmt.strip().lower().replace("excel", "xlsx")
        for fmt in raw.split(",") if fmt.strip()
    ]