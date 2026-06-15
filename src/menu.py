def show_menu():
    print("\nHousehold Inventory Tracker v0.1")
    print("1. Add item")
    print("2. View all items")
    print("3. Search items")
    print("4. Update item")
    print("5. Delete item")
    print("6. View low-stock items")
    print("7. Save and exit")


def get_user_choice():
    return input("Choose an option: ").strip()