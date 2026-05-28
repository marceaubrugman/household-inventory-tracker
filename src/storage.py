import json
from pathlib import Path


def load_inventory(filename="inventory.json"):
    path = Path(filename)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Warning: inventory file is invalid. Starting with an empty inventory.")
        return []


def save_inventory(items, filename="inventory.json"):
    path = Path(filename)

    with path.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=4)