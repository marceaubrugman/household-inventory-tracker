def show_menu():
    """Display the main application menu."""
    print("\nHousehold Inventory Tracker v0.2.0")
    print("1. Add item")
    print("2. View all items")
    print("3. Search items")
    print("4. Update item")
    print("5. Delete item")
    print("6. View low-stock items")
    print("7. Exit")


def get_user_choice():
    """Return the user's stripped menu selection."""
    return input("Choose an option: ").strip()