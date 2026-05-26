from src.validators import get_non_empty_input, get_non_negative_int
from src.display import print_items


def get_next_id(items):
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def add_item(items):
    print("\nAdd New Item")

    name = get_non_empty_input("Name: ")
    category = get_non_empty_input("Category: ")
    location = get_non_empty_input("Location: ")
    quantity = get_non_negative_int("Quantity: ")
    minimum_quantity = get_non_negative_int("Minimum quantity: ")
    notes = input("Notes: ").strip()

    item = {
        "id": get_next_id(items),
        "name": name,
        "category": category,
        "location": location,
        "quantity": quantity,
        "minimum_quantity": minimum_quantity,
        "notes": notes,
    }

    items.append(item)
    print(f"Item '{name}' added successfully.")


def list_items(items):
    print("\nInventory Items")

    if not items:
        print("No items in inventory.")
        return

    print_items(items)

def search_items(items, search_term):
    pass

def update_item(items, item_id, updated_data):
    pass

def delete_item(items, item_id):
    pass

def get_low_stock_items(items):
    pass