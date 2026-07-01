from typing import Any

from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routers import items as items_router


client = TestClient(app)


def test_update_item_returns_updated_item(
    monkeypatch,
) -> None:
    """Verify that supplied fields are sent to the service."""
    received_call: dict[str, Any] = {}

    def fake_update_inventory_item(
        item_id: int,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        received_call["item_id"] = item_id
        received_call["updates"] = updates

        return {
            "id": item_id,
            "name": "Rice",
            "category": "Food",
            "quantity": 8,
            "minimum_quantity": 1,
            "location": "Pantry",
            "notes": "Basmati",
        }

    monkeypatch.setattr(
        items_router.item_service,
        "update_inventory_item",
        fake_update_inventory_item,
    )

    response = client.patch(
        "/items/7",
        json={"quantity": 8},
    )

    assert response.status_code == 200
    assert received_call == {
        "item_id": 7,
        "updates": {"quantity": 8},
    }
    assert response.json()["quantity"] == 8


def test_update_item_returns_404_when_missing(
    monkeypatch,
) -> None:
    """Verify that updating a missing item returns 404."""

    def fake_update_inventory_item(
        item_id: int,
        updates: dict[str, Any],
    ) -> None:
        return None

    monkeypatch.setattr(
        items_router.item_service,
        "update_inventory_item",
        fake_update_inventory_item,
    )

    response = client.patch(
        "/items/999999",
        json={"quantity": 8},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_update_item_rejects_negative_quantity() -> None:
    """Verify that negative quantities are rejected."""
    response = client.patch(
        "/items/7",
        json={"quantity": -1},
    )

    assert response.status_code == 422


def test_update_item_rejects_empty_body() -> None:
    """Verify that an update must contain at least one field."""
    response = client.patch(
        "/items/7",
        json={},
    )

    assert response.status_code == 422


def test_update_item_rejects_null_required_field() -> None:
    """Verify that required item fields cannot be cleared."""
    response = client.patch(
        "/items/7",
        json={"name": None},
    )

    assert response.status_code == 422


def test_update_item_allows_notes_to_be_cleared(
    monkeypatch,
) -> None:
    """Verify that explicit null clears optional notes."""
    received_updates: dict[str, Any] = {}

    def fake_update_inventory_item(
        item_id: int,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        received_updates.update(updates)

        return {
            "id": item_id,
            "name": "Rice",
            "category": "Food",
            "quantity": 3,
            "minimum_quantity": 1,
            "location": "Pantry",
            "notes": None,
        }

    monkeypatch.setattr(
        items_router.item_service,
        "update_inventory_item",
        fake_update_inventory_item,
    )

    response = client.patch(
        "/items/7",
        json={"notes": None},
    )

    assert response.status_code == 200
    assert received_updates == {"notes": None}
    assert response.json()["notes"] is None