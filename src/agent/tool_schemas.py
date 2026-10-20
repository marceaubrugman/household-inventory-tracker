
"""Read-only tool definitions exposed to the AI model."""

READ_TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "search_items",
        "description": (
            "Search household inventory for items matching "
            "a name, category, or location. "
            "Returns up to five candidate items."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for.",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_item",
        "description": (
            "Retrieve current inventory details for "
            "one item using its unique numeric ID."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "integer",
                    "description": "Unique inventory item ID.",
                },
            },
            "required": ["item_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]
