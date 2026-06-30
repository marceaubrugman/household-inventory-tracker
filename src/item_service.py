from typing import Any

from src.item_repository import (
    create_item,
    get_all_items,
    get_item_by_id,
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