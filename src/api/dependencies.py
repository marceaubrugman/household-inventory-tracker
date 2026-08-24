from typing import Annotated, Any, Literal

from fastapi import HTTPException, Path, Query, status

from src.item_service import (
    find_inventory_item,
    list_inventory_items,
    list_low_stock_inventory_items,
    search_inventory_items,
)


def fetch_items(
    search: Annotated[
        str | None,
        Query(
            description="Literal search across name, category, and location",
        ),
    ] = None,
    sort: Annotated[
        Literal["name", "category", "location", "quantity"],
        Query(
            description="Approved inventory sort order",
        ),
    ] = "name",
    low_stock: Annotated[
        bool,
        Query(
            description="Return only quantity-tracked items at or below minimum quantity",
        ),
    ] = False,
) -> list[dict[str, Any]]:
    """Fetch inventory items according to the requested query options."""
    if search is not None and low_stock:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Search and low-stock filtering cannot be combined.",
        )

    if low_stock:
        return list_low_stock_inventory_items(sort)

    if search is None:
        return list_inventory_items(sort)

    normalized_search = search.strip()

    if not normalized_search:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Search term cannot be blank.",
        )

    return search_inventory_items(
        normalized_search,
        sort,
    )


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