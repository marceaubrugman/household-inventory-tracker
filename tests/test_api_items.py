from typing import Any

from fastapi.testclient import TestClient

from src.api.dependencies import fetch_all_items
from src.api.main import app


client = TestClient(app)


def fake_fetch_all_items() -> list[dict[str, Any]]:
    """Return predictable inventory data without using PostgreSQL."""
    return [
        {
            "id": 1,
            "name": "Pasta",
            "category": "Food",
            "quantity": 4,
            "minimum_quantity": 2,
            "location": "Pantry",
            "notes": "Whole wheat",
            "created_at": "2026-06-29T08:00:00+00:00",
            "updated_at": "2026-06-29T08:00:00+00:00",
        }
    ]


def test_get_items_returns_inventory_items() -> None:
    """Verify that the API returns the public item representation."""
    app.dependency_overrides[fetch_all_items] = fake_fetch_all_items

    try:
        response = client.get("/items")
    finally:
        app.dependency_overrides.pop(fetch_all_items, None)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Pasta",
            "category": "Food",
            "quantity": 4,
            "minimum_quantity": 2,
            "location": "Pantry",
            "notes": "Whole wheat",
        }
    ]