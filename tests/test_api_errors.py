from typing import NoReturn

from fastapi.testclient import TestClient

from src.api.dependencies import fetch_all_items
from src.api.main import app
from src.database import DatabaseConfigurationError


client = TestClient(app)


def raise_database_configuration_error() -> NoReturn:
    """Simulate unavailable database configuration."""
    raise DatabaseConfigurationError("DATABASE_URL is not configured.")


def test_items_returns_503_when_database_is_not_configured() -> None:
    """Verify that database configuration errors become safe API responses."""
    app.dependency_overrides[fetch_all_items] = (
        raise_database_configuration_error
    )

    try:
        response = client.get("/items")
    finally:
        app.dependency_overrides.pop(fetch_all_items, None)

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database service is unavailable."
    }