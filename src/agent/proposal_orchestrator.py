
"""Run bounded, draft-only AI consumption interactions."""

import json
from typing import Any

from src.agent import dispatcher
from src.agent.dispatcher import ToolRequestError
from src.agent.tool_schemas import READ_TOOL_SCHEMAS
from src.agent.workflow import prepare_consumption_draft


PROPOSAL_TOOL_SCHEMA = {
    "type": "function",
    "name": "propose_consumption",
    "description": (
        "Prepare a draft proposal to consume a quantity "
        "of an inventory item. Never update inventory."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "item_id": {
                "type": "integer",
                "description": "Existing inventory item ID.",
            },
            "amount": {
                "type": "integer",
                "description": "Positive quantity consumed.",
            },
        },
        "required": ["item_id", "amount"],
        "additionalProperties": False,
    },
    "strict": True,
}

SEARCH_TOOL_SCHEMA = next(
    schema
    for schema in READ_TOOL_SCHEMAS
    if schema["name"] == "search_items"
)

INSTRUCTIONS = (
    "You help prepare inventory consumption drafts. "
    "Use search_items to discover inventory item IDs "
    "rather than guessing them. "
    "Only request propose_consumption when the user "
    "reports consuming inventory. "
    "Never claim inventory was updated or approved."
)


def single_tool_call(response: Any) -> Any | None:
    """Accept exactly one function call in a completed response."""

    if response.status != "completed":
        return None

    calls = [
        item
        for item in response.output
        if getattr(item, "type", None) == "function_call"
    ]

    if len(calls) != 1:
        return None

    return calls[0]


def prepare_agent_consumption_draft(
    original_request: str,
    client: Any,
) -> dict[str, Any] | None:
    """Use at most two model requests to prepare a guarded draft."""

    first_response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=INSTRUCTIONS,
        input=original_request,
        tools=[
            SEARCH_TOOL_SCHEMA,
            PROPOSAL_TOOL_SCHEMA,
        ],
        tool_choice="auto",
        parallel_tool_calls=False,
        max_output_tokens=300,
        store=False,
    )

    first_call = single_tool_call(first_response)

    if first_call is None:
        return None

    if first_call.name == "propose_consumption":
        return prepare_consumption_draft(
            original_request=original_request,
            arguments_json=first_call.arguments,
        )

    if first_call.name != "search_items":
        raise ToolRequestError(
            "Unsupported proposal tool."
        )

    search_result = dispatcher.dispatch_read_tool(
        first_call.name,
        first_call.arguments,
    )

    continuation_input = [
        {
            "role": "user",
            "content": original_request,
        },
        {
            "type": "function_call",
            "name": first_call.name,
            "arguments": first_call.arguments,
            "call_id": first_call.call_id,
        },
        {
            "type": "function_call_output",
            "call_id": first_call.call_id,
            "output": json.dumps(search_result),
        },
    ]

    second_response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=INSTRUCTIONS,
        input=continuation_input,
        tools=[PROPOSAL_TOOL_SCHEMA],
        tool_choice="auto",
        parallel_tool_calls=False,
        max_output_tokens=300,
        store=False,
    )

    second_call = single_tool_call(second_response)

    if second_call is None:
        return None

    if second_call.name != "propose_consumption":
        raise ToolRequestError(
            "Unsupported proposal tool."
        )

    return prepare_consumption_draft(
        original_request=original_request,
        arguments_json=second_call.arguments,
    )
