from typing import Any

from fastapi.testclient import TestClient

from src.api.dependencies import fetch_item_by_id
from src.api.main import app


client = TestClient(app)


def fake_existing_item(item_id: int) -> dict[str, Any]:
    """Return one predictable item without using PostgreSQL."""
    assert item_id == 1

    return {
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


def fake_missing_item(item_id: int) -> None:
    """Simulate an item that does not exist."""
    assert item_id == 999999
    return None


def test_get_item_returns_inventory_item() -> None:
    """Verify that an existing item is returned."""
    app.dependency_overrides[fetch_item_by_id] = fake_existing_item

    try:
        response = client.get("/items/1")
    finally:
        app.dependency_overrides.pop(fetch_item_by_id, None)

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Pasta",
        "category": "Food",
        "quantity": 4,
        "minimum_quantity": 2,
        "location": "Pantry",
        "notes": "Whole wheat",
    }


def test_get_item_returns_404_when_item_does_not_exist() -> None:
    """Verify that a missing item produces a 404 response."""
    app.dependency_overrides[fetch_item_by_id] = fake_missing_item

    try:
        response = client.get("/items/999999")
    finally:
        app.dependency_overrides.pop(fetch_item_by_id, None)

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_get_item_rejects_non_integer_id() -> None:
    """Verify that a non-integer item ID is rejected."""
    response = client.get("/items/banana")

    assert response.status_code == 422


def test_get_item_rejects_non_positive_id() -> None:
    """Verify that item IDs must be positive integers."""
    response = client.get("/items/0")

    assert response.status_code == 422