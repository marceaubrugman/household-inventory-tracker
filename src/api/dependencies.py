from typing import Any

from src.item_repository import get_all_items


def fetch_all_items() -> list[dict[str, Any]]:
    """Fetch all inventory items through the repository layer."""
    return get_all_items()