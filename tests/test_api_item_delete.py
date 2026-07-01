from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routers import items as items_router


client = TestClient(app)


def test_delete_item_returns_204(
    monkeypatch,
) -> None:
    """Verify that deleting an existing item returns no content."""
    received_ids: list[int] = []

    def fake_delete_inventory_item(item_id: int) -> bool:
        received_ids.append(item_id)
        return True

    monkeypatch.setattr(
        items_router.item_service,
        "delete_inventory_item",
        fake_delete_inventory_item,
    )

    response = client.delete("/items/7")

    assert response.status_code == 204
    assert response.content == b""
    assert received_ids == [7]


def test_delete_item_returns_404_when_missing(
    monkeypatch,
) -> None:
    """Verify that deleting a missing item returns 404."""

    def fake_delete_inventory_item(item_id: int) -> bool:
        assert item_id == 999999
        return False

    monkeypatch.setattr(
        items_router.item_service,
        "delete_inventory_item",
        fake_delete_inventory_item,
    )

    response = client.delete("/items/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_delete_item_rejects_zero_id(
    monkeypatch,
) -> None:
    """Verify that zero is rejected before reaching the service."""
    service_was_called = False

    def fake_delete_inventory_item(_item_id: int) -> bool:
        nonlocal service_was_called
        service_was_called = True
        return True

    monkeypatch.setattr(
        items_router.item_service,
        "delete_inventory_item",
        fake_delete_inventory_item,
    )

    response = client.delete("/items/0")

    assert response.status_code == 422
    assert service_was_called is False


def test_delete_item_rejects_zero_id(
    monkeypatch,
) -> None:
    """Verify that zero is rejected before reaching the service."""
    service_was_called = False

    def fake_delete_inventory_item(_item_id: int) -> bool:
        nonlocal service_was_called
        service_was_called = True
        return True

    monkeypatch.setattr(
        items_router.item_service,
        "delete_inventory_item",
        fake_delete_inventory_item,
    )

    response = client.delete("/items/0")

    assert response.status_code == 422
    assert service_was_called is False