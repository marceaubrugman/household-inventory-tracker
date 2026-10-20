
"""Build inventory proposals without changing stored state."""

from typing import Any

from src.item_service import find_inventory_item


def build_consumption_proposal(
    item_id: int,
    amount: int,
) -> dict[str, Any]:
    """Prepare a validated consumption proposal without executing it."""

    if type(item_id) is not int or item_id <= 0:
        raise ValueError(
            "Item ID must be a positive integer."
        )

    if type(amount) is not int or amount <= 0:
        raise ValueError(
            "Consumption amount must be a positive whole number."
        )

    item = find_inventory_item(item_id)

    if item is None:
        raise ValueError("Item not found.")

    if item["tracking_mode"] != "quantity":
        raise ValueError(
            "Consumption requires a quantity-tracked item."
        )

    current_quantity = item["quantity"]

    if amount > current_quantity:
        raise ValueError(
            "Consumption amount exceeds available stock."
        )

    proposed_quantity = current_quantity - amount

    return {
        "status": "draft",
        "operation": "consume",
        "item_id": item["id"],
        "item_name": item["name"],
        "amount": amount,
        "expected_quantity": current_quantity,
        "proposed_quantity": proposed_quantity,
    }
