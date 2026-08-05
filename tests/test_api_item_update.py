from typing import Any

import pytest
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
            "tracking_mode": "quantity",
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
    assert response.json()["tracking_mode"] == "quantity"

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
            "tracking_mode": "quantity",
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


def test_update_item_switches_to_individual_tracking(
    monkeypatch,
) -> None:
    """Verify an item can switch to individual tracking."""
    received_updates: dict[str, Any] = {}

    def fake_update_inventory_item(
        item_id: int,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        assert item_id == 7
        received_updates.update(updates)

        return {
            "id": 7,
            "name": "Cordless drill",
            "category": "Tools",
            "location": "Garage",
            "tracking_mode": "individual",
            "quantity": None,
            "minimum_quantity": None,
            "notes": "Blue carrying case",
        }

    monkeypatch.setattr(
        items_router.item_service,
        "update_inventory_item",
        fake_update_inventory_item,
    )

    payload = {
        "tracking_mode": "individual",
        "quantity": None,
        "minimum_quantity": None,
    }

    response = client.patch(
        "/items/7",
        json=payload,
    )

    assert response.status_code == 200
    assert received_updates == payload
    assert response.json() == {
        "id": 7,
        "name": "Cordless drill",
        "category": "Tools",
        "location": "Garage",
        "tracking_mode": "individual",
        "quantity": None,
        "minimum_quantity": None,
        "notes": "Blue carrying case",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {
            "tracking_mode": "individual",
        },
        {
            "tracking_mode": "individual",
            "quantity": 1,
            "minimum_quantity": 0,
        },
        {
            "tracking_mode": "quantity",
            "quantity": None,
            "minimum_quantity": None,
        },
        {
            "tracking_mode": "quantity",
            "quantity": 1,
        },
        {
            "quantity": None,
        },
    ],
)


def test_update_item_rejects_invalid_tracking_mode_transition(
    monkeypatch,
    payload,
) -> None:
    """Verify incomplete or inconsistent mode changes are rejected."""
    service_was_called = False

    def fake_update_inventory_item(
        item_id: int,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        nonlocal service_was_called
        service_was_called = True
        return {}

    monkeypatch.setattr(
        items_router.item_service,
        "update_inventory_item",
        fake_update_inventory_item,
    )

    response = client.patch(
        "/items/7",
        json=payload,
    )

    assert response.status_code == 422
    assert service_was_called is False
