from typing import Any

from src.item_repository import (
    create_item,
    get_all_items,
    get_item_by_id,
    update_item,
)


def list_inventory_items() -> list[dict[str, Any]]:
    """Return all inventory items."""
    return get_all_items()


def find_inventory_item(item_id: int) -> dict[str, Any] | None:
    """Return one inventory item by ID, or None when it does not exist."""
    return get_item_by_id(item_id)


def create_inventory_item(
    *,
    name: str,
    category: str,
    quantity: int,
    minimum_quantity: int,
    location: str,
    notes: str | None,
) -> dict[str, Any]:
    """Create and return an inventory item."""
    return create_item(
        name=name,
        category=category,
        quantity=quantity,
        minimum_quantity=minimum_quantity,
        location=location,
        notes=notes,
    )


UPDATABLE_ITEM_FIELDS = {
    "name",
    "category",
    "quantity",
    "minimum_quantity",
    "location",
    "notes",
}


def update_inventory_item(
    item_id: int,
    updates: dict[str, Any],
) -> dict[str, Any] | None:
    """Apply partial changes and return the updated item."""
    current_item = get_item_by_id(item_id)

    if current_item is None:
        return None

    unexpected_fields = set(updates) - UPDATABLE_ITEM_FIELDS

    if unexpected_fields:
        raise ValueError(
            f"Unsupported update fields: {unexpected_fields}"
        )

    merged_item = {
        field: current_item[field]
        for field in UPDATABLE_ITEM_FIELDS
    }
    merged_item.update(updates)

    update_item(
        item_id=item_id,
        name=merged_item["name"],
        category=merged_item["category"],
        quantity=merged_item["quantity"],
        minimum_quantity=merged_item["minimum_quantity"],
        location=merged_item["location"],
        notes=merged_item["notes"],
    )

    return get_item_by_id(item_id)