from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.api.dependencies import fetch_all_items, fetch_item_by_id
from src import item_service
from src.api.schemas import (
    ItemCreate,
    ItemResponse,
    ItemUpdate,
)




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


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an inventory item",
)
def create_item_endpoint(
    item_data: ItemCreate,
) -> dict[str, Any]:
    """Create and return an inventory item."""
    return item_service.create_inventory_item(
        **item_data.model_dump()
    )


@router.patch(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Update an inventory item",
)
def update_item_endpoint(
    item_id: Annotated[
        int,
        Path(
            ge=1,
            description="Unique inventory item ID",
        ),
    ],
    item_data: ItemUpdate,
) -> dict[str, Any]:
    """Partially update and return an inventory item."""
    updated_item = item_service.update_inventory_item(
        item_id=item_id,
        updates=item_data.model_dump(exclude_unset=True),
    )

    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return updated_item