from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import fetch_all_items, fetch_item_by_id
from src.api.schemas import ItemResponse




router = APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.get(
    "",
    response_model=list[ItemResponse],
    summary="List inventory items",
)
def list_items(
    items: Annotated[
        list[dict[str, Any]],
        Depends(fetch_all_items),
    ],
) -> list[dict[str, Any]]:
    """Return all inventory items."""
    return items


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get an inventory item",
)
def get_item(
    item: Annotated[
        dict[str, Any] | None,
        Depends(fetch_item_by_id),
    ],
) -> dict[str, Any]:
    """Return one inventory item by ID."""
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return item