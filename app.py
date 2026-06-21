from src.inventory_workflows import (
    add_item,
    delete_item,
    list_items,
    search_inventory,
    show_low_stock_items,
    update_item,
)
from src.menu import get_user_choice, show_menu


def main():
    while True:
        show_menu()
        choice = get_user_choice()

        if choice == "1":
            add_item()

        elif choice == "2":
            list_items()

        elif choice == "3":
            search_inventory()

        elif choice == "4":
            update_item()

        elif choice == "5":
            delete_item()

        elif choice == "6":
            show_low_stock_items()

        elif choice == "7":
            print("Goodbye.")
            break

        else:
            print(
                "Invalid choice. "
                "Please enter a number from 1 to 7."
            )


if __name__ == "__main__":
    main()