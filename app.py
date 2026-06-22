import psycopg

from src.database import DatabaseConfigurationError
from src.inventory_workflows import (
    add_item,
    delete_item,
    list_items,
    search_inventory,
    show_low_stock_items,
    update_item,
)
from src.menu import get_user_choice, show_menu


def run_database_action(action):
    """Run one database action and handle expected database failures."""

    try:
        action()

    except DatabaseConfigurationError as error:
        print(f"\nDatabase configuration error: {error}")

    except psycopg.Error:
        print(
            "\nThe database operation could not be completed. "
            "Check that PostgreSQL is running and try again."
        )


def main():
    """Run the PostgreSQL-backed inventory application."""

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == "1":
            run_database_action(add_item)

        elif choice == "2":
            run_database_action(list_items)

        elif choice == "3":
            run_database_action(search_inventory)

        elif choice == "4":
            run_database_action(update_item)

        elif choice == "5":
            run_database_action(delete_item)

        elif choice == "6":
            run_database_action(show_low_stock_items)

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
