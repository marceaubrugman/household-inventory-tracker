from typing import Annotated, Any

from fastapi import Path

from src.item_repository import get_all_items, get_item_by_id


def fetch_all_items() -> list[dict[str, Any]]:
    """Fetch all inventory items through the repository layer."""
    return get_all_items()


def fetch_item_by_id(
    item_id: Annotated[
        int,
        Path(
            ge=1,
            description="Unique inventory item ID",
        ),
    ],
) -> dict[str, Any] | None:
    """Fetch one inventory item through the repository layer."""
    return get_item_by_id(item_id)