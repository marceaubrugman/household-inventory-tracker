from src.menu import show_menu, get_user_choice
from src.inventory_service import (
    add_item,
    list_items,
    search_items,
    update_item,
    delete_item,
    get_low_stock_items,
    sort_items,
)
from src.display import print_items
from src.storage import load_inventory, save_inventory


def main():

    items = load_inventory()

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == "1":
           if add_item(items):
               save_inventory(items)
        elif choice == "2":
            print("\nSort by:")
            print("1. Name")
            print("2. Category")
            print("3. Location")
            print("4. Quantity")

            sort_choice = input("Choose sorting option: ").strip()

            sort_map = {
                "1": "name",
                "2": "category",
                "3": "location",
                "4": "quantity",
            }

            sort_key = sort_map.get(sort_choice, "name")
            sorted_items = sort_items(items, sort_key)
            list_items(sorted_items)
        elif choice == "3":
            search_term = input("Enter search term (name, category, or location): ").strip()

            if not search_term:
                print("Search term cannot be empty.")
            else:
                matching_items = search_items(items, search_term)

                if not matching_items:
                    print(f"No items found for search term '{search_term}'.")
                else:
                    print(f"\nSearch results for '{search_term}':")
                    print_items(matching_items)
        elif choice == "4":
            if update_item(items):
                save_inventory(items)
        elif choice == "5":
            if delete_item(items):
                save_inventory(items)
        elif choice == "6":
            low_stock_items = get_low_stock_items(items)

            if not low_stock_items:
                print("No low-stock items found.")
            else:
                print("\nLow-stock items:")
                print_items(low_stock_items)
        elif choice == "7":
            save_inventory(items)
            print("Inventory saved. Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()