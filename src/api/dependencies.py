from typing import Annotated, Any

from fastapi import Path

from src.item_service import find_inventory_item, list_inventory_items


def fetch_all_items() -> list[dict[str, Any]]:
    """Fetch all inventory items through the service layer."""
    return list_inventory_items()


def fetch_item_by_id(
    item_id: Annotated[
        int,
        Path(
            ge=1,
            description="Unique inventory item ID",
        ),
    ],
) -> dict[str, Any] | None:
    """Fetch one inventory item through the service layer."""
    return find_inventory_item(item_id)