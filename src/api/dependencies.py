from typing import Annotated, Any

from fastapi import HTTPException, Path, Query, status

from src.item_service import (
    find_inventory_item,
    list_inventory_items,
    search_inventory_items,
)


def fetch_items(
    search: Annotated[
        str | None,
        Query(
            description="Literal search across name, category, and location",
        ),
    ] = None,
) -> list[dict[str, Any]]:
    """Fetch all items or items matching an optional search term."""
    if search is None:
        return list_inventory_items()

    normalized_search = search.strip()

    if not normalized_search:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Search term cannot be blank.",
        )

    return search_inventory_items(normalized_search)


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