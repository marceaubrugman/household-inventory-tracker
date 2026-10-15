
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.item_service import search_inventory_items, find_inventory_item


MAX_SEARCH_RESULTS = 5


class SearchItemsInput(BaseModel):
    """Validate input for the inventory search tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    query: str = Field(min_length=1, max_length=100)


def search_items(query: str) -> dict[str, Any]:
    """Return a bounded, read-only inventory search result."""

    request = SearchItemsInput(query=query)

    found = search_inventory_items(
        request.query,
        sort_key="name",
        limit=MAX_SEARCH_RESULTS + 1,
        offset=0,
    )

    matches = [
        {
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "location": item["location"],
            "tracking_mode": item["tracking_mode"],
            "quantity": item["quantity"],
        }
        for item in found[:MAX_SEARCH_RESULTS]
    ]

    return {
        "matches": matches,
        "has_more": len(found) > MAX_SEARCH_RESULTS,
    }



class GetItemInput(BaseModel):
    """Validate input for the item lookup tool."""

    model_config = ConfigDict(extra="forbid")

    item_id: int = Field(gt=0, strict=True)


def get_item(item_id: int) -> dict[str, Any]:
    """Retrieve one inventory item without modifying it."""

    request = GetItemInput(item_id=item_id)

    item = find_inventory_item(request.item_id)

    if item is None:
        return {
            "status": "not_found",
            "item": None,
        }

    return {
        "status": "found",
        "item": {
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "location": item["location"],
            "tracking_mode": item["tracking_mode"],
            "quantity": item["quantity"],
            "minimum_quantity": item["minimum_quantity"],
        },
    }
