
from typing import Any

from pydantic import ValidationError

from src.agent import tools


class ToolRequestError(ValueError):
    """A tool request is unsupported or invalid."""


def dispatch_read_tool(
    name: str,
    arguments_json: str,
) -> dict[str, Any]:
    """Execute only explicitly approved read-only tools."""

    if name not in {"search_items", "get_item"}:
        raise ToolRequestError("Tool is not allowed.")

    try:
        if name == "search_items":
            request = tools.SearchItemsInput.model_validate_json(
                arguments_json
            )
            return tools.search_items(request.query)

        request = tools.GetItemInput.model_validate_json(
            arguments_json
        )
        return tools.get_item(request.item_id)

    except ValidationError as error:
        raise ToolRequestError(
            "Invalid tool arguments."
        ) from error
