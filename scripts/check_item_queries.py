from src.display import print_item, print_items
from src.item_repository import get_item_by_id, search_items
from src.validators import get_positive_int_or_cancel


def check_item_lookup():
    print("\nFind PostgreSQL item by ID")

    item_id = get_positive_int_or_cancel("Enter item ID")

    if item_id is None:
        print("Item lookup cancelled.")
        return

    item = get_item_by_id(item_id)

    if item is None:
        print(f"No item found with ID {item_id}.")
        return

    print("\nItem found:")
    print_item(item)


def check_item_search():
    print("\nSearch PostgreSQL inventory")

    search_term = input(
        "Enter search term (name, category, or location): "
    ).strip()

    if not search_term:
        print("Search term cannot be empty.")
        return

    matching_items = search_items(search_term)

    if not matching_items:
        print(f"No items found matching '{search_term}'.")
        return

    print(f"\nSearch results for '{search_term}':")
    print_items(matching_items)


def main():
    while True:
        print("\nRepository query checks")
        print("1. Find item by ID")
        print("2. Search items")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            check_item_lookup()
        elif choice == "2":
            check_item_search()
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()