
"""Coordinate guarded inventory consumption proposals."""

from typing import Any

from pydantic import ValidationError

from src.agent.dispatcher import (
    ToolRequestError,
    dispatch_proposal_tool,
)
from src.agent.intent import (
    resolve_consumption_amount,
    extract_consumption_item_description,
)

from src.agent.resolver import resolve_consumption_item
from src.agent.tools import ProposeConsumptionInput


def prepare_consumption_draft(
    original_request: str,
    arguments_json: str,
) -> dict[str, Any] | None:
    """Prepare a draft only when independently verified values agree."""

    resolved_amount = resolve_consumption_amount(
        original_request
    )

    if resolved_amount is None:
        return None

    item_description = extract_consumption_item_description(
        original_request
    )

    if item_description is None:
        return None

    resolved_item_id = resolve_consumption_item(
        original_request,
        exact_description=item_description,
    )

    if resolved_item_id is None:
        return None

    try:
        request = ProposeConsumptionInput.model_validate_json(
            arguments_json
        )
    except ValidationError as error:
        raise ToolRequestError(
            "Invalid tool arguments."
        ) from error

    if request.amount != resolved_amount:
        raise ToolRequestError(
            "Proposed amount does not match resolved consumption."
        )

    return dispatch_proposal_tool(
        "propose_consumption",
        arguments_json,
        resolved_item_id=resolved_item_id,
    )
