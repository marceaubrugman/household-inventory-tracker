from src.display import print_item
from src.item_repository import (
    delete_item as delete_item_from_database,
    get_item_by_id,
    update_item as update_item_in_database,
)
from src.validators import (
    get_optional_non_empty_input,
    get_optional_non_negative_int,
    get_optional_notes,
    get_positive_int_or_cancel,
    normalize_text,
)


def check_update_item():
    print("\nUpdate PostgreSQL item")

    item_id = get_positive_int_or_cancel("Enter item ID to update")

    if item_id is None:
        print("Update cancelled.")
        return

    current_item = get_item_by_id(item_id)

    if current_item is None:
        print(f"No item found with ID {item_id}.")
        return

    print("\nCurrent item:")
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

    updated_item = update_item_in_database(
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
            "The item could not be updated because it no longer exists."
        )
        return

    print("\nItem updated successfully:")
    print_item(updated_item)


def check_delete_item():
    print("\nDelete PostgreSQL item")

    item_id = get_positive_int_or_cancel("Enter item ID to delete")

    if item_id is None:
        print("Deletion cancelled.")
        return

    current_item = get_item_by_id(item_id)

    if current_item is None:
        print(f"No item found with ID {item_id}.")
        return

    print("\nItem to delete:")
    print_item(current_item)

    confirmation = input(
        "Are you sure you want to delete this item? (y/n): "
    ).strip().lower()

    if confirmation != "y":
        print("Deletion cancelled.")
        return

    deleted_item = delete_item_from_database(item_id)

    if deleted_item is None:
        print(
            "The item could not be deleted because it no longer exists."
        )
        return

    print("\nItem deleted successfully:")
    print_item(deleted_item)


def main():
    while True:
        print("\nPostgreSQL update and delete checks")
        print("1. Update item")
        print("2. Delete item")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            check_update_item()
        elif choice == "2":
            check_delete_item()
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()