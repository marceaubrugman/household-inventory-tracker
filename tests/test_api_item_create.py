from typing import Any

from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routers import items as items_router


client = TestClient(app)


def test_create_item_returns_201_and_created_item(
    monkeypatch,
) -> None:
    """Verify that valid item data creates an inventory item."""
    received_data: dict[str, Any] = {}

    def fake_create_inventory_item(
        **item_data: Any,
    ) -> dict[str, Any]:
        received_data.update(item_data)

        return {
            "id": 12,
            **item_data,
            "created_at": "2026-06-30T10:00:00+00:00",
            "updated_at": "2026-06-30T10:00:00+00:00",
        }

    monkeypatch.setattr(
        items_router.item_service,
        "create_inventory_item",
        fake_create_inventory_item,
    )

    payload = {
        "name": "Rice",
        "category": "Food",
        "quantity": 3,
        "minimum_quantity": 1,
        "location": "Pantry",
        "notes": "Basmati",
    }

    response = client.post("/items", json=payload)

    assert response.status_code == 201
    assert received_data == payload
    assert response.json() == {
        "id": 12,
        **payload,
    }


def test_create_item_rejects_negative_quantity(
    monkeypatch,
) -> None:
    """Verify that invalid quantities never reach the service."""
    service_was_called = False

    def fake_create_inventory_item(
        **_item_data: Any,
    ) -> dict[str, Any]:
        nonlocal service_was_called
        service_was_called = True
        return {}

    monkeypatch.setattr(
        items_router.item_service,
        "create_inventory_item",
        fake_create_inventory_item,
    )

    response = client.post(
        "/items",
        json={
            "name": "Rice",
            "category": "Food",
            "quantity": -1,
            "minimum_quantity": 1,
            "location": "Pantry",
            "notes": None,
        },
    )

    assert response.status_code == 422
    assert service_was_called is False



def test_create_item_rejects_blank_name(
    monkeypatch,
) -> None:
    """Verify that blank item names never reach the service."""
    service_was_called = False

    def fake_create_inventory_item(
        **_item_data: Any,
    ) -> dict[str, Any]:
        nonlocal service_was_called
        service_was_called = True
        return {}

    monkeypatch.setattr(
        items_router.item_service,
        "create_inventory_item",
        fake_create_inventory_item,
    )

    response = client.post(
        "/items",
        json={
            "name": "   ",
            "category": "Food",
            "quantity": 3,
            "minimum_quantity": 1,
            "location": "Pantry",
            "notes": None,
        },
    )

    assert response.status_code == 422
    assert service_was_called is False