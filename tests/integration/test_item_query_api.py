import pytest
from fastapi.testclient import TestClient

from src.api.main import app


pytestmark = pytest.mark.integration

client = TestClient(app)


def test_api_searches_inventory_items():
    """Verify search works through the full API and PostgreSQL stack."""

    rice_payload = {
        "name": "Brown rice",
        "category": "Food",
        "location": "Pantry",
        "tracking_mode": "quantity",
        "quantity": 10,
        "minimum_quantity": 3,
        "notes": "Basmati",
    }

    soap_payload = {
        "name": "Dish soap",
        "category": "Cleaning",
        "location": "Kitchen cabinet",
        "tracking_mode": "quantity",
        "quantity": 2,
        "minimum_quantity": 1,
        "notes": "",
    }

    rice_response = client.post(
        "/items",
        json=rice_payload,
    )
    soap_response = client.post(
        "/items",
        json=soap_payload,
    )

    assert rice_response.status_code == 201
    assert soap_response.status_code == 201

    search_response = client.get(
        "/items",
        params={"search": "rice"},
    )

    assert search_response.status_code == 200

    results = search_response.json()

    assert len(results) == 1
    assert results[0]["name"] == "Brown rice"


def test_api_sorts_inventory_by_quantity():
    """Verify quantity sorting works through the full API stack."""

    high_quantity_payload = {
        "name": "Brown rice",
        "category": "Food",
        "location": "Pantry",
        "tracking_mode": "quantity",
        "quantity": 10,
        "minimum_quantity": 3,
        "notes": "",
    }

    low_quantity_payload = {
        "name": "Dish soap",
        "category": "Cleaning",
        "location": "Kitchen cabinet",
        "tracking_mode": "quantity",
        "quantity": 2,
        "minimum_quantity": 1,
        "notes": "",
    }

    assert client.post(
        "/items",
        json=high_quantity_payload,
    ).status_code == 201

    assert client.post(
        "/items",
        json=low_quantity_payload,
    ).status_code == 201

    response = client.get(
        "/items",
        params={"sort": "quantity"},
    )

    assert response.status_code == 200

    results = response.json()

    assert [
        item["quantity"]
        for item in results
    ] == [2, 10]


def test_api_combines_search_and_quantity_sort():
    """Verify search and sorting compose through PostgreSQL."""

    items = [
        {
            "name": "Brown rice",
            "category": "Food",
            "location": "Pantry",
            "tracking_mode": "quantity",
            "quantity": 10,
            "minimum_quantity": 3,
            "notes": "",
        },
        {
            "name": "Dish soap",
            "category": "Cleaning",
            "location": "Kitchen cabinet",
            "tracking_mode": "quantity",
            "quantity": 2,
            "minimum_quantity": 1,
            "notes": "",
        },
        {
            "name": "Hammer",
            "category": "Tools",
            "location": "Garage",
            "tracking_mode": "quantity",
            "quantity": 1,
            "minimum_quantity": 0,
            "notes": "",
        },
    ]

    for payload in items:
        assert client.post(
            "/items",
            json=payload,
        ).status_code == 201

    response = client.get(
        "/items",
        params={
            "search": "i",
            "sort": "quantity",
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert [
        item["name"]
        for item in results
    ] == [
        "Dish soap",
        "Brown rice",
    ]


def test_api_quantity_sort_places_individual_items_last():
    """Verify NULL quantities sort after numeric quantities."""

    quantity_item = {
        "name": "Dish soap",
        "category": "Cleaning",
        "location": "Kitchen cabinet",
        "tracking_mode": "quantity",
        "quantity": 2,
        "minimum_quantity": 1,
        "notes": "",
    }

    individual_item = {
        "name": "Cordless drill",
        "category": "Tools",
        "location": "Garage",
        "tracking_mode": "individual",
        "quantity": None,
        "minimum_quantity": None,
        "notes": "",
    }

    assert client.post(
        "/items",
        json=individual_item,
    ).status_code == 201

    assert client.post(
        "/items",
        json=quantity_item,
    ).status_code == 201

    response = client.get(
        "/items",
        params={"sort": "quantity"},
    )

    assert response.status_code == 200

    results = response.json()

    assert [
        item["name"]
        for item in results
    ] == [
        "Dish soap",
        "Cordless drill",
    ]
