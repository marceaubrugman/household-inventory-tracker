from typing import Annotated, Any

from fastapi import APIRouter, Depends

from src.api.dependencies import fetch_all_items
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