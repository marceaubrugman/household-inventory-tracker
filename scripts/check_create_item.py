from src.display import print_item
from src.item_repository import create_item
from src.validators import (
    get_non_empty_input,
    get_non_negative_int,
    normalize_text,
)


def main():
    print("\nCreate PostgreSQL inventory item")

    name = normalize_text(get_non_empty_input("Name: "))
    category = normalize_text(get_non_empty_input("Category: "))
    location = normalize_text(get_non_empty_input("Location: "))
    quantity = get_non_negative_int("Quantity: ")
    minimum_quantity = get_non_negative_int("Minimum quantity: ")
    notes = input("Notes: ").strip()

    created_item = create_item(
        name=name,
        category=category,
        location=location,
        quantity=quantity,
        minimum_quantity=minimum_quantity,
        notes=notes,
    )

    print("\nItem created successfully in PostgreSQL:")
    print_item(created_item)


if __name__ == "__main__":
    main()