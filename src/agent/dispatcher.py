
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


def dispatch_proposal_tool(
    name: str,
    arguments_json: str,
    *,
    resolved_item_id: int | None,
) -> dict[str, Any]:
    """Dispatch a draft-only tool after trusted item resolution."""

    if name != "propose_consumption":
        raise ToolRequestError("Tool is not allowed.")

    if (
        type(resolved_item_id) is not int
        or resolved_item_id <= 0
    ):
        raise ToolRequestError(
            "Item identity is unresolved."
        )

    try:
        request = tools.ProposeConsumptionInput.model_validate_json(
            arguments_json
        )
    except ValidationError as error:
        raise ToolRequestError(
            "Invalid tool arguments."
        ) from error

    if request.item_id != resolved_item_id:
        raise ToolRequestError(
            "Proposed item does not match resolved item."
        )

    return tools.propose_consumption(
        item_id=request.item_id,
        amount=request.amount,
    )
