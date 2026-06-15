def print_item(item):
    notes = item["notes"] if item["notes"] else "-"

    print(f"ID: {item['id']}")
    print(f"Name: {item['name']}")
    print(f"Category: {item['category']}")
    print(f"Location: {item['location']}")
    print(f"Quantity: {item['quantity']}")
    print(f"Minimum quantity: {item['minimum_quantity']}")
    print(f"Notes: {notes}")
    print("-" * 30)


def print_items(items):
    for item in items:
        print_item(item)