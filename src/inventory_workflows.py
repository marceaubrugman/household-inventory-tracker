from src import item_repository
from src.display import print_item, print_items
from src.validators import (
    get_non_empty_input,
    get_non_negative_int,
    get_optional_non_empty_input,
    get_optional_non_negative_int,
    get_optional_notes,
    get_positive_int_or_cancel,
    normalize_text,
)


SORT_OPTIONS = {
    "1": "name",
    "2": "category",
    "3": "location",
    "4": "quantity",
}


def _choose_sort_key():
    print("\nSort by:")
    print("1. Name")
    print("2. Category")
    print("3. Location")
    print("4. Quantity")

    choice = input("Choose sorting option: ").strip()
    sort_key = SORT_OPTIONS.get(choice)

    if sort_key is None:
        print("Invalid choice. Sorting by name.")
        return "name"

    return sort_key


def add_item():
    print("\nAdd New Item")

    name = normalize_text(get_non_empty_input("Name: "))
    category = normalize_text(get_non_empty_input("Category: "))
    location = normalize_text(get_non_empty_input("Location: "))
    quantity = get_non_negative_int("Quantity: ")
    minimum_quantity = get_non_negative_int(
        "Minimum quantity: "
    )
    notes = input("Notes: ").strip()

    created_item = item_repository.create_item(
        name=name,
        category=category,
        location=location,
        quantity=quantity,
        minimum_quantity=minimum_quantity,
        notes=notes,
    )

    print("\nItem added successfully:")
    print_item(created_item)


def list_items():
    print("\nInventory Items")

    sort_key = _choose_sort_key()
    items = item_repository.get_all_items(sort_key)

    if not items:
        print("No items in inventory.")
        return

    print_items(items)


def search_inventory():
    print("\nSearch Inventory")

    search_term = input(
        "Enter search term (name, category, or location): "
    ).strip()

    if not search_term:
        print("Search term cannot be empty.")
        return

    matching_items = item_repository.search_items(search_term)

    if not matching_items:
        print(
            f"No items found for search term "
            f"'{search_term}'."
        )
        return

    print(f"\nSearch results for '{search_term}':")
    print_items(matching_items)


def update_item():
    print("\nUpdate Item")

    item_id = get_positive_int_or_cancel(
        "Enter item ID to update: "
    )

    if item_id is None:
        print("Update cancelled.")
        return

    current_item = item_repository.get_item_by_id(item_id)

    if current_item is None:
        print(f"No item found with ID {item_id}.")
        return

    print("\nCurrent item details:")
    print_item(current_item)
    print("Press Enter to keep the current value.")

    name = normalize_text(
        get_optional_non_empty_input(
            "Name",
            current_item["name"],
        )
    )

    category = normalize_text(
        get_optional_non_empty_input(
            "Category",
            current_item["category"],
        )
    )

    location = normalize_text(
        get_optional_non_empty_input(
            "Location",
            current_item["location"],
        )
    )

    quantity = get_optional_non_negative_int(
        "Quantity",
        current_item["quantity"],
    )

    minimum_quantity = get_optional_non_negative_int(
        "Minimum quantity",
        current_item["minimum_quantity"],
    )

    notes = get_optional_notes(
        "Notes",
        current_item["notes"],
    )

    updated_item = item_repository.update_item(
        item_id=item_id,
        name=name,
        category=category,
        location=location,
        quantity=quantity,
        minimum_quantity=minimum_quantity,
        notes=notes,
    )

    if updated_item is None:
        print(
            "The item could not be updated because "
            "it no longer exists."
        )
        return

    print("\nItem updated successfully:")
    print_item(updated_item)


def delete_item():
    print("\nDelete Item")

    item_id = get_positive_int_or_cancel(
        "Enter item ID to delete: "
    )

    if item_id is None:
        print("Deletion cancelled.")
        return

    current_item = item_repository.get_item_by_id(item_id)

    if current_item is None:
        print(f"No item found with ID {item_id}.")
        return

    print("\nItem to delete:")
    print_item(current_item)

    confirmation = input(
        "Are you sure you want to delete this item? "
        "(y/n): "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        return

    deleted_item = item_repository.delete_item(item_id)

    if deleted_item is None:
        print(
            "The item could not be deleted because "
            "it no longer exists."
        )
        return

    print("\nItem deleted successfully:")
    print_item(deleted_item)


def show_low_stock_items():
    print("\nLow-stock Items")

    sort_key = _choose_sort_key()
    low_stock_items = item_repository.get_low_stock_items(
        sort_key
    )

    if not low_stock_items:
        print("No low-stock items found.")
        return

    print_items(low_stock_items)