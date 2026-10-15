
from src.agent.tool_schemas import READ_TOOL_SCHEMAS


def test_read_tool_names_are_allowlisted():
    names = {
        tool["name"]
        for tool in READ_TOOL_SCHEMAS
    }

    assert names == {"search_items", "get_item"}


def test_read_tool_schemas_are_strict():
    for tool in READ_TOOL_SCHEMAS:
        parameters = tool["parameters"]

        assert tool["type"] == "function"
        assert tool["strict"] is True
        assert parameters["type"] == "object"
        assert parameters["additionalProperties"] is False
        assert set(parameters["required"]) == set(
            parameters["properties"]
        )


def test_read_tool_argument_types():
    by_name = {
        tool["name"]: tool
        for tool in READ_TOOL_SCHEMAS
    }

    search_properties = by_name[
        "search_items"
    ]["parameters"]["properties"]

    item_properties = by_name[
        "get_item"
    ]["parameters"]["properties"]

    assert search_properties["query"]["type"] == "string"
    assert item_properties["item_id"]["type"] == "integer"
