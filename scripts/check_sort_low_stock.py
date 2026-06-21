from src.display import print_items
from src.item_repository import (
    get_all_items,
    get_low_stock_items,
)


SORT_OPTIONS = {
    "1": "name",
    "2": "category",
    "3": "location",
    "4": "quantity",
}


def choose_sort_key():
    print("\nSort by:")
    print("1. Name")
    print("2. Category")
    print("3. Location")
    print("4. Quantity")

    choice = input("Choose a sorting option: ").strip()

    sort_key = SORT_OPTIONS.get(choice)

    if sort_key is None:
        print("Invalid choice. Sorting by name.")
        return "name"

    return sort_key


def check_all_items():
    print("\nList PostgreSQL inventory")

    sort_key = choose_sort_key()
    items = get_all_items(sort_key)

    if not items:
        print("The database contains no inventory items.")
        return

    print(f"\nInventory sorted by {sort_key}:")
    print_items(items)


def check_low_stock_items():
    print("\nList low-stock PostgreSQL items")

    sort_key = choose_sort_key()
    items = get_low_stock_items(sort_key)

    if not items:
        print("No low-stock items found.")
        return

    print(f"\nLow-stock items sorted by {sort_key}:")
    print_items(items)


def main():
    while True:
        print("\nPostgreSQL inventory view checks")
        print("1. List all items")
        print("2. List low-stock items")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            check_all_items()
        elif choice == "2":
            check_low_stock_items()
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()