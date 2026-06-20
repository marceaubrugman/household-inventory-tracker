from src.display import print_items
from src.item_repository import get_all_items


def main():
    items = get_all_items()

    if not items:
        print("The database contains no inventory items.")
        return

    print("\nItems loaded from PostgreSQL:")
    print_items(items)


if __name__ == "__main__":
    main()