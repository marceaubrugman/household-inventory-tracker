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
    ) -> list[dict[str, Any]]:
        assert search_term == "Pasta"

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
    ) -> list[dict[str, Any]]:
        assert search_term == "Pasta"
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
