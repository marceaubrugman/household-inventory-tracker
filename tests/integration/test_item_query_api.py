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


def test_api_returns_only_low_stock_quantity_items():
    """Verify low-stock filtering through the full API stack."""

    items = [
        {
            "name": "Toilet paper",
            "category": "Bathroom",
            "location": "Closet",
            "tracking_mode": "quantity",
            "quantity": 1,
            "minimum_quantity": 4,
            "notes": "",
        },
        {
            "name": "Pasta",
            "category": "Food",
            "location": "Pantry",
            "tracking_mode": "quantity",
            "quantity": 8,
            "minimum_quantity": 3,
            "notes": "",
        },
        {
            "name": "Cordless drill",
            "category": "Tools",
            "location": "Garage",
            "tracking_mode": "individual",
            "quantity": None,
            "minimum_quantity": None,
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
        params={"low_stock": "true"},
    )

    assert response.status_code == 200

    results = response.json()

    assert [
        item["name"]
        for item in results
    ] == [
        "Toilet paper",
    ]


def test_api_sorts_low_stock_items_by_quantity():
    """Verify low-stock results preserve approved sorting."""

    items = [
        {
            "name": "Dishwasher tablets",
            "category": "Cleaning",
            "location": "Kitchen",
            "tracking_mode": "quantity",
            "quantity": 2,
            "minimum_quantity": 2,
            "notes": "",
        },
        {
            "name": "Toilet paper",
            "category": "Bathroom",
            "location": "Closet",
            "tracking_mode": "quantity",
            "quantity": 1,
            "minimum_quantity": 4,
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
            "low_stock": "true",
            "sort": "quantity",
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert [
        item["quantity"]
        for item in results
    ] == [1, 2]


def test_api_paginates_inventory_items():
    """Verify limit and offset through the full API stack."""

    for name in [
        "Apples",
        "Bananas",
        "Carrots",
        "Dates",
    ]:
        payload = {
            "name": name,
            "category": "Food",
            "location": "Pantry",
            "tracking_mode": "quantity",
            "quantity": 1,
            "minimum_quantity": 0,
            "notes": "",
        }

        assert client.post(
            "/items",
            json=payload,
        ).status_code == 201

    response = client.get(
        "/items",
        params={
            "limit": 2,
            "offset": 2,
        },
    )

    assert response.status_code == 200

    assert [
        item["name"]
        for item in response.json()
    ] == [
        "Carrots",
        "Dates",
    ]


def test_api_combines_search_sort_and_pagination():
    """Verify search, sorting, and pagination compose."""

    items = [
        {
            "name": "Rice one",
            "category": "Food",
            "location": "Pantry",
            "tracking_mode": "quantity",
            "quantity": 4,
            "minimum_quantity": 0,
            "notes": "",
        },
        {
            "name": "Rice two",
            "category": "Food",
            "location": "Pantry",
            "tracking_mode": "quantity",
            "quantity": 1,
            "minimum_quantity": 0,
            "notes": "",
        },
        {
            "name": "Rice three",
            "category": "Food",
            "location": "Pantry",
            "tracking_mode": "quantity",
            "quantity": 3,
            "minimum_quantity": 0,
            "notes": "",
        },
        {
            "name": "Rice four",
            "category": "Food",
            "location": "Pantry",
            "tracking_mode": "quantity",
            "quantity": 2,
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
            "search": "rice",
            "sort": "quantity",
            "limit": 2,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    assert [
        item["quantity"]
        for item in response.json()
    ] == [
        2,
        3,
    ]


def test_api_combines_low_stock_sort_and_pagination():
    """Verify low-stock filtering, sorting, and pagination compose."""

    items = [
        {
            "name": "Toilet paper",
            "category": "Bathroom",
            "location": "Closet",
            "tracking_mode": "quantity",
            "quantity": 1,
            "minimum_quantity": 4,
            "notes": "",
        },
        {
            "name": "Dishwasher tablets",
            "category": "Cleaning",
            "location": "Kitchen",
            "tracking_mode": "quantity",
            "quantity": 2,
            "minimum_quantity": 2,
            "notes": "",
        },
        {
            "name": "Pasta",
            "category": "Food",
            "location": "Pantry",
            "tracking_mode": "quantity",
            "quantity": 8,
            "minimum_quantity": 3,
            "notes": "",
        },
        {
            "name": "Cordless drill",
            "category": "Tools",
            "location": "Garage",
            "tracking_mode": "individual",
            "quantity": None,
            "minimum_quantity": None,
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
            "low_stock": "true",
            "sort": "quantity",
            "limit": 1,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 1
    assert results[0]["name"] == "Dishwasher tablets"
    assert results[0]["quantity"] == 2