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
