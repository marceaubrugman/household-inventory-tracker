from typing import Any

from src import item_service


def test_list_inventory_items_returns_repository_result(
    monkeypatch,
) -> None:
    """Verify that listing items delegates to the repository."""
    expected_items = [{"id": 1}, {"id": 2}]

    def fake_get_all_items() -> list[dict[str, Any]]:
        return expected_items

    monkeypatch.setattr(
        item_service,
        "get_all_items",
        fake_get_all_items,
    )

    result = item_service.list_inventory_items()

    assert result == expected_items


def test_find_inventory_item_forwards_item_id(
    monkeypatch,
) -> None:
    """Verify that item lookup forwards the requested ID."""
    requested_ids: list[int] = []

    def fake_get_item_by_id(item_id: int) -> dict[str, Any]:
        requested_ids.append(item_id)
        return {"id": item_id}

    monkeypatch.setattr(
        item_service,
        "get_item_by_id",
        fake_get_item_by_id,
    )

    result = item_service.find_inventory_item(7)

    assert requested_ids == [7]
    assert result == {"id": 7}


def test_find_inventory_item_returns_none_when_missing(
    monkeypatch,
) -> None:
    """Verify that a missing repository item remains None."""

    def fake_get_item_by_id(_item_id: int) -> None:
        return None

    monkeypatch.setattr(
        item_service,
        "get_item_by_id",
        fake_get_item_by_id,
    )

    result = item_service.find_inventory_item(999999)

    assert result is None