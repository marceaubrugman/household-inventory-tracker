from src.menu import show_menu, get_user_choice

def main():
    while True:
        show_menu()
        choice = get_user_choice()

        if choice == "1":
            print("Add item selected.")
        elif choice == "2":
            print("View all items selected.")
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