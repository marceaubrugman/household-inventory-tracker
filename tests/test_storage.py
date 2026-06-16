from src.storage import load_inventory, save_inventory


def test_save_and_load_inventory_round_trip(tmp_path):
    items = [
        {
            "id": 1,
            "name": "Rice",
            "category": "Food",
            "location": "Pantry",
            "quantity": 2,
            "minimum_quantity": 3,
            "notes": "Buy this week",
        }
    ]

    test_file = tmp_path / "inventory.json"

    save_inventory(items, test_file)
    loaded_items = load_inventory(test_file)

    assert loaded_items == items