from src.menu import show_menu, get_user_choice
from src.inventory_service import add_item, list_items


def main():

    items = []

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == "1":
            add_item(items)
        elif choice == "2":
            list_items(items)
        elif choice == "3":
            print("Search items selected.")
        elif choice == "4":
            print("Update item selected.")
        elif choice == "5":
            print("Delete item selected.")
        elif choice == "6":
            print("View low-stock items selected.")
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()