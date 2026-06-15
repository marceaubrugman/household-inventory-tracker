from src.validators import (
    get_non_empty_input,
    get_non_negative_int,
    get_positive_int,
    get_positive_int_or_cancel,
    get_optional_non_empty_input,
    get_optional_non_negative_int,

)
from src.display import print_items, print_item


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
    return True


def list_items(items):
    print("\nInventory Items")

    if not items:
        print("No items in inventory.")
        return

    print_items(items)


def search_items(items, search_term):
    normalized_search_term = search_term.strip().lower()

    return [
        item
        for item in items
        if normalized_search_term in item["name"].lower()
    ]


def find_item_by_id(items, item_id):
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def update_item(items):
    print("\nUpdate Item")

    if not items:
        print("No items in inventory.")
        return False

    item_id = get_positive_int_or_cancel("Enter item ID to update: ")

    if item_id is None:
        print("Update cancelled.")
        return False

    item = find_item_by_id(items, item_id)

    if item is None:
        print(f"No item found with ID {item_id}.")
        return False

    print("\nCurrent item details:")
    print_item(item)
    print("Press Enter to keep the current value.")

    item["name"] = get_optional_non_empty_input("Name", item["name"])
    item["category"] = get_optional_non_empty_input("Category", item["category"])
    item["location"] = get_optional_non_empty_input("Location", item["location"])
    item["quantity"] = get_optional_non_negative_int("Quantity", item["quantity"])
    item["minimum_quantity"] = get_optional_non_negative_int(
        "Minimum quantity", item["minimum_quantity"]
    )

    current_notes = item["notes"] if item["notes"] else "-"
    new_notes = input(f"Notes [{current_notes}]: ").strip()
    item["notes"] = item["notes"] if new_notes == "" else new_notes

    print(f"Item ID {item_id} updated successfully.")
    return True


def delete_item(items):
    print("\nDelete Item")

    if not items:
        print("No items in inventory.")
        return False

    item_id = get_positive_int_or_cancel("Enter item ID to delete: ")

    if item_id is None:
        print("Deletion cancelled.")
        return False

    item = find_item_by_id(items, item_id)

    if item is None:
        print(f"No item found with ID {item_id}.")
        return False

    print("\nItem to delete:")
    print_item(item)

    confirmation = input("Are you sure you want to delete this item? (y/n): ").strip().lower()

    if confirmation == "y":
        items.remove(item)
        print(f"Item ID {item_id} deleted successfully.")
        return True
    else:
        print("Deletion cancelled.")
        return False


def get_low_stock_items(items):
    return [
        item
        for item in items
        if item["quantity"] <= item["minimum_quantity"]
    ]