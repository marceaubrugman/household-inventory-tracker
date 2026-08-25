from typing import Any

from fastapi.testclient import TestClient

from src.api.dependencies import fetch_items
from src.api.main import app

from src.api import dependencies


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
            "tracking_mode": "quantity",
            "notes": "Whole wheat",
            "created_at": "2026-06-29T08:00:00+00:00",
            "updated_at": "2026-06-29T08:00:00+00:00",
        }
    ]


def test_get_items_returns_inventory_items() -> None:
    """Verify that the API returns the public item representation."""
    app.dependency_overrides[fetch_items] = fake_fetch_all_items

    try:
        response = client.get("/items")
    finally:
        app.dependency_overrides.pop(fetch_items, None)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Pasta",
            "category": "Food",
            "quantity": 4,
            "minimum_quantity": 2,
            "location": "Pantry",
            "tracking_mode": "quantity",
            "notes": "Whole wheat",
        }
    ]


def test_get_items_with_search_returns_matching_items(
    monkeypatch,
) -> None:
    """Verify that a search query returns matching inventory items."""

    def fake_search_inventory_items(
            search_term: str,
            sort_key: str = "name",
            limit: int | None = None,
            offset: int = 0,
    ) -> list[dict[str, Any]]:
        assert search_term == "Pasta"
        assert sort_key == "name"

        return [
            {
                "id": 1,
                "name": "Pasta",
                "category": "Food",
                "quantity": 4,
                "minimum_quantity": 2,
                "location": "Pantry",
                "tracking_mode": "quantity",
                "notes": "Whole wheat",
                "created_at": "2026-06-29T08:00:00+00:00",
                "updated_at": "2026-06-29T08:00:00+00:00",
            }
        ]

    monkeypatch.setattr(
        dependencies,
        "search_inventory_items",
        fake_search_inventory_items,
    )

    response = client.get("/items?search=Pasta")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Pasta",
            "category": "Food",
            "quantity": 4,
            "minimum_quantity": 2,
            "location": "Pantry",
            "tracking_mode": "quantity",
            "notes": "Whole wheat",
        }
    ]


def test_get_items_search_trims_surrounding_whitespace(
    monkeypatch,
) -> None:
    """Verify that surrounding search whitespace is removed."""

    def fake_search_inventory_items(
        search_term: str,
        sort_key: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        assert search_term == "Pasta"
        assert sort_key == "name"
        return []

    monkeypatch.setattr(
        dependencies,
        "search_inventory_items",
        fake_search_inventory_items,
    )

    response = client.get(
        "/items",
        params={"search": "   Pasta   "},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_items_search_rejects_blank_term() -> None:
    """Verify that an explicitly blank search term is rejected."""

    response = client.get(
        "/items",
        params={"search": ""},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Search term cannot be blank."
    }


def test_get_items_search_rejects_whitespace_only_term() -> None:
    """Verify that whitespace-only search input is rejected."""

    response = client.get(
        "/items",
        params={"search": "   "},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Search term cannot be blank."
    }


def test_get_items_with_sort_forwards_sort_key(
    monkeypatch,
) -> None:
    """Verify that an approved sort key reaches the list service."""

    received_sort_keys: list[str] = []

    def fake_list_inventory_items(
        sort_key: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        received_sort_keys.append(sort_key)
        return []

    monkeypatch.setattr(
        dependencies,
        "list_inventory_items",
        fake_list_inventory_items,
    )

    response = client.get(
        "/items",
        params={"sort": "quantity"},
    )

    assert response.status_code == 200
    assert response.json() == []
    assert received_sort_keys == ["quantity"]


def test_get_items_with_search_and_sort_forwards_both(
    monkeypatch,
) -> None:
    """Verify that search and sort are forwarded together."""

    received_arguments: list[tuple[str, str]] = []

    def fake_search_inventory_items(
        search_term: str,
        sort_key: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        received_arguments.append(
            (search_term, sort_key)
        )
        return []

    monkeypatch.setattr(
        dependencies,
        "search_inventory_items",
        fake_search_inventory_items,
    )

    response = client.get(
        "/items",
        params={
            "search": "rice",
            "sort": "quantity",
        },
    )

    assert response.status_code == 200
    assert response.json() == []
    assert received_arguments == [
        ("rice", "quantity")
    ]


def test_get_items_rejects_unsupported_sort_key() -> None:
    """Verify that unsupported sort keys are rejected."""

    response = client.get(
        "/items",
        params={"sort": "banana"},
    )

    assert response.status_code == 422


def test_get_items_with_low_stock_forwards_filter(
    monkeypatch,
) -> None:
    """Verify that low-stock filtering reaches the low-stock service."""

    received_sort_keys: list[str] = []

    def fake_list_low_stock_inventory_items(
        sort_key: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        received_sort_keys.append(sort_key)
        return []

    monkeypatch.setattr(
        dependencies,
        "list_low_stock_inventory_items",
        fake_list_low_stock_inventory_items,
    )

    response = client.get(
        "/items",
        params={"low_stock": "true"},
    )

    assert response.status_code == 200
    assert response.json() == []
    assert received_sort_keys == ["name"]


def test_get_items_with_low_stock_and_sort_forwards_both(
    monkeypatch,
) -> None:
    """Verify that low-stock filtering preserves the requested sort order."""

    received_sort_keys: list[str] = []

    def fake_list_low_stock_inventory_items(
        sort_key: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        received_sort_keys.append(sort_key)
        return []

    monkeypatch.setattr(
        dependencies,
        "list_low_stock_inventory_items",
        fake_list_low_stock_inventory_items,
    )

    response = client.get(
        "/items",
        params={
            "low_stock": "true",
            "sort": "quantity",
        },
    )

    assert response.status_code == 200
    assert response.json() == []
    assert received_sort_keys == ["quantity"]


def test_get_items_with_low_stock_false_lists_normal_inventory(
    monkeypatch,
) -> None:
    """Verify that low_stock=false preserves normal listing behavior."""

    received_sort_keys: list[str] = []

    def fake_list_inventory_items(
        sort_key: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        received_sort_keys.append(sort_key)
        return []

    monkeypatch.setattr(
        dependencies,
        "list_inventory_items",
        fake_list_inventory_items,
    )

    response = client.get(
        "/items",
        params={"low_stock": "false"},
    )

    assert response.status_code == 200
    assert response.json() == []
    assert received_sort_keys == ["name"]


def test_get_items_rejects_search_with_low_stock() -> None:
    """Verify that search and low-stock filtering cannot be combined."""

    response = client.get(
        "/items",
        params={
            "search": "rice",
            "low_stock": "true",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Search and low-stock filtering cannot be combined."
    }


def test_get_items_forwards_pagination(
    monkeypatch,
) -> None:
    """Verify that limit and offset reach the listing service."""

    received_arguments = []

    def fake_list_inventory_items(
        sort_key: str = "name",
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        received_arguments.append(
            (sort_key, limit, offset)
        )
        return []

    monkeypatch.setattr(
        dependencies,
        "list_inventory_items",
        fake_list_inventory_items,
    )

    response = client.get(
        "/items",
        params={
            "limit": 20,
            "offset": 40,
        },
    )

    assert response.status_code == 200
    assert response.json() == []
    assert received_arguments == [
        ("name", 20, 40)
    ]


def test_get_items_rejects_limit_below_one() -> None:
    """Verify that limit must be at least one."""

    response = client.get(
        "/items",
        params={"limit": 0},
    )

    assert response.status_code == 422


def test_get_items_rejects_limit_above_one_hundred() -> None:
    """Verify that limit cannot exceed one hundred."""

    response = client.get(
        "/items",
        params={"limit": 101},
    )

    assert response.status_code == 422


def test_get_items_rejects_negative_offset() -> None:
    """Verify that offset cannot be negative."""

    response = client.get(
        "/items",
        params={"offset": -1},
    )

    assert response.status_code == 422
