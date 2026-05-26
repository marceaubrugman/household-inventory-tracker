def get_next_id(items):
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def add_item(items):
    print("\nAdd New Item")

    name = input("Name: ").strip()
    category = input("Category: ").strip()
    location = input("Location: ").strip()
    quantity = int(input("Quantity: ").strip())
    minimum_quantity = int(input("Minimum quantity: ").strip())
    notes = input("Notes: ").strip()

    item = {
        "id": get_next_id(items),
        "name": name,
        "category": category,
        "location": location,
        "quantity": quantity,
        "minimum_quantity": minimum_quantity,
        "notes": notes,
    }

    items.append(item)
    print(f"Item '{name}' added successfully.")


def list_items(items):
    print("\nInventory Items")

    if not items:
        print("No items in inventory.")
        return

    for item in items:
        print(
            f"ID: {item['id']} | "
            f"Name: {item['name']} | "
            f"Category: {item['category']} | "
            f"Location: {item['location']} | "
            f"Quantity: {item['quantity']} | "
            f"Minimum: {item['minimum_quantity']} | "
            f"Notes: {item['notes']}"
        )

def search_items(items, search_term):
    pass

def update_item(items, item_id, updated_data):
    pass

def delete_item(items, item_id):
    pass

def get_low_stock_items(items):
    pass