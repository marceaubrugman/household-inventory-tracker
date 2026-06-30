from typing import Any

from src.item_repository import get_all_items, get_item_by_id


def list_inventory_items() -> list[dict[str, Any]]:
    """Return all inventory items."""
    return get_all_items()


def find_inventory_item(item_id: int) -> dict[str, Any] | None:
    """Return one inventory item by ID, or None when it does not exist."""
    return get_item_by_id(item_id)