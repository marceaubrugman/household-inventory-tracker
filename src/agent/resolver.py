
"""Conservatively resolve inventory identity for proposals."""

import re

from src.item_service import list_inventory_items


MAX_RESOLUTION_ITEMS = 50


def resolve_consumption_item(
    original_request: str,
    *,
    exact_description: str | None = None,
) -> int | None:
    """Resolve one explicitly identified item, or return None."""

    request_words = set(
        re.findall(r"\w+", original_request.casefold())
    )

    if not request_words:
        return None

    if exact_description is not None:
        description_words = sorted(
            re.findall(r"\w+", exact_description.casefold())
        )

        if not description_words:
            return None

    items = list_inventory_items(
        sort_key="name",
        limit=MAX_RESOLUTION_ITEMS + 1,
        offset=0,
    )

    if len(items) > MAX_RESOLUTION_ITEMS:
        return None


    matching_ids = []

    for item in items:
        name_tokens = re.findall(
            r"\w+",
            item["name"].casefold(),
        )

        if exact_description is not None:
            matches = (
                bool(name_tokens)
                and sorted(name_tokens) == description_words
            )
        else:
            matches = (
                bool(name_tokens)
                and set(name_tokens).issubset(request_words)
            )

        if matches:
            matching_ids.append(item["id"])


    if len(matching_ids) != 1:
        return None

    return matching_ids[0]
