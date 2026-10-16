
import pytest

from src.agent import dispatcher
from src.agent.dispatcher import (
    ToolRequestError,
    dispatch_read_tool,
)


def test_dispatch_search(monkeypatch):
    def fake_search(query):
        assert query == "dishwasher"
        return {"matches": [], "has_more": False}

    monkeypatch.setattr(
        dispatcher.tools, "search_items", fake_search
    )

    result = dispatch_read_tool(
        "search_items",
        '{"query": " dishwasher "}',
    )

    assert result == {
        "matches": [],
        "has_more": False,
    }


def test_dispatch_get_item(monkeypatch):
    def fake_get(item_id):
        assert item_id == 17
        return {"status": "not_found", "item": None}

    monkeypatch.setattr(
        dispatcher.tools, "get_item", fake_get
    )

    result = dispatch_read_tool(
        "get_item",
        '{"item_id": 17}',
    )

    assert result["status"] == "not_found"


def test_dispatch_rejects_unknown_tool():
    with pytest.raises(
        ToolRequestError, match="not allowed"
    ):
        dispatch_read_tool(
            "delete_item",
            '{"item_id": 17}',
        )


@pytest.mark.parametrize(
    "arguments",
    [
        '{"item_id": "17"}',
        '{"item_id": 0}',
        '{"item_id": 17, "unexpected": true}',
        "not-json",
    ],
)
def test_dispatch_rejects_invalid_arguments(arguments):
    with pytest.raises(
        ToolRequestError, match="Invalid tool arguments"
    ):
        dispatch_read_tool("get_item", arguments)



def test_read_dispatcher_rejects_consumption_proposal():
    """Read-only workflows must not invoke proposal tools."""

    with pytest.raises(
        ToolRequestError,
        match="Tool is not allowed",
    ):
        dispatch_read_tool(
            "propose_consumption",
            '{"item_id": 17, "amount": 2}',
        )
