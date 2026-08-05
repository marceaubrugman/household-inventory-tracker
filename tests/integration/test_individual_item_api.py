import pytest
from fastapi.testclient import TestClient

from src.api.main import app


pytestmark = pytest.mark.integration

client = TestClient(app)


def test_api_creates_and_retrieves_individual_item():
    """Verify individual creation works through the full API stack."""
    payload = {
        "name": "Cordless drill",
        "category": "Tools",
        "location": "Garage",
        "tracking_mode": "individual",
        "quantity": None,
        "minimum_quantity": None,
        "notes": "Blue carrying case",
    }

    create_response = client.post(
        "/items",
        json=payload,
    )

    assert create_response.status_code == 201

    created_item = create_response.json()
    item_id = created_item["id"]

    assert created_item == {
        "id": item_id,
        **payload,
    }

    get_response = client.get(f"/items/{item_id}")

    assert get_response.status_code == 200
    assert get_response.json() == created_item


def test_api_defaults_legacy_payload_to_quantity_tracking():
    """Verify older create payloads remain quantity-tracked."""
    payload = {
        "name": "Brown rice",
        "category": "Food",
        "location": "Pantry",
        "quantity": 10,
        "minimum_quantity": 3,
        "notes": "Basmati",
    }

    response = client.post(
        "/items",
        json=payload,
    )

    assert response.status_code == 201

    created_item = response.json()

    assert created_item == {
        "id": created_item["id"],
        **payload,
        "tracking_mode": "quantity",
    }


def test_api_switches_quantity_item_to_individual_tracking():
    """Verify a quantity item can become an individual asset."""
    create_response = client.post(
        "/items",
        json={
            "name": "Cordless drill",
            "category": "Tools",
            "location": "Garage",
            "tracking_mode": "quantity",
            "quantity": 1,
            "minimum_quantity": 0,
            "notes": "Blue carrying case",
        },
    )

    assert create_response.status_code == 201

    item_id = create_response.json()["id"]

    update_response = client.patch(
        f"/items/{item_id}",
        json={
            "tracking_mode": "individual",
            "quantity": None,
            "minimum_quantity": None,
        },
    )

    assert update_response.status_code == 200

    updated_item = update_response.json()

    assert updated_item == {
        "id": item_id,
        "name": "Cordless drill",
        "category": "Tools",
        "location": "Garage",
        "tracking_mode": "individual",
        "quantity": None,
        "minimum_quantity": None,
        "notes": "Blue carrying case",
    }

    get_response = client.get(f"/items/{item_id}")

    assert get_response.status_code == 200
    assert get_response.json() == updated_item


def test_api_switches_individual_item_to_quantity_tracking():
    """Verify an individual asset can become quantity-tracked."""
    create_response = client.post(
        "/items",
        json={
            "name": "Printer paper",
            "category": "Office",
            "location": "Study",
            "tracking_mode": "individual",
            "quantity": None,
            "minimum_quantity": None,
            "notes": "Unopened box",
        },
    )

    assert create_response.status_code == 201

    item_id = create_response.json()["id"]

    update_response = client.patch(
        f"/items/{item_id}",
        json={
            "tracking_mode": "quantity",
            "quantity": 5,
            "minimum_quantity": 2,
        },
    )

    assert update_response.status_code == 200

    updated_item = update_response.json()

    assert updated_item == {
        "id": item_id,
        "name": "Printer paper",
        "category": "Office",
        "location": "Study",
        "tracking_mode": "quantity",
        "quantity": 5,
        "minimum_quantity": 2,
        "notes": "Unopened box",
    }

    get_response = client.get(f"/items/{item_id}")

    assert get_response.status_code == 200
    assert get_response.json() == updated_item
