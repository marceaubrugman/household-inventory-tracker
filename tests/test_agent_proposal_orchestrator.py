
from types import SimpleNamespace

from src.agent import (
    proposal_orchestrator,
    proposals,
    resolver,
    dispatcher,
)

import pytest

from src.agent.dispatcher import ToolRequestError


def test_model_tool_call_produces_guarded_draft(monkeypatch):
    """A model request must pass Python's proposal safeguards."""

    inventory = [
        {"id": 17, "name": "Dishwasher tablets, Classic"},
        {"id": 18, "name": "Dishwasher tablets, Eco"},
    ]

    monkeypatch.setattr(
        resolver,
        "list_inventory_items",
        lambda **kwargs: inventory,
    )

    monkeypatch.setattr(
        proposals,
        "find_inventory_item",
        lambda item_id: {
            "id": 17,
            "name": "Dishwasher tablets, Classic",
            "tracking_mode": "quantity",
            "quantity": 24,
        },
    )

    fake_response = SimpleNamespace(
        status="completed",
        output=[
            SimpleNamespace(
                type="function_call",
                name="propose_consumption",
                arguments='{"item_id": 17, "amount": 2}',
                call_id="call_1",
            )
        ],
    )

    requests = []

    def fake_create(**kwargs):
        requests.append(kwargs)
        return fake_response

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(create=fake_create)
    )

    result = (
        proposal_orchestrator.prepare_agent_consumption_draft(
            original_request=(
                "I used two Classic dishwasher tablets."
            ),
            client=fake_client,
        )
    )

    assert result == {
        "status": "draft",
        "operation": "consume",
        "item_id": 17,
        "item_name": "Dishwasher tablets, Classic",
        "amount": 2,
        "expected_quantity": 24,
        "proposed_quantity": 22,
    }

    assert len(requests) == 1


def test_search_result_precedes_model_proposal(monkeypatch):
    """The model can search inventory before proposing consumption."""

    read_calls = []

    def fake_read_tool(name, arguments_json):
        read_calls.append((name, arguments_json))

        assert name == "search_items"

        return {
            "items": [
                {"id": 17, "name": "Dishwasher tablets, Classic"},
                {"id": 18, "name": "Dishwasher tablets, Eco"},
            ],
            "has_more": False,
        }

    monkeypatch.setattr(
        dispatcher,
        "dispatch_read_tool",
        fake_read_tool,
    )


    def fake_prepare_draft(original_request, arguments_json):
        assert original_request == (
            "I used two Classic dishwasher tablets."
        )
        assert arguments_json == (
            '{"item_id": 17, "amount": 2}'
        )

        return {"status": "draft", "item_id": 17}

    monkeypatch.setattr(
        proposal_orchestrator,
        "prepare_consumption_draft",
        fake_prepare_draft,
    )

    fake_responses = iter(
        [
            SimpleNamespace(
                status="completed",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="search_items",
                        arguments='{"query": "dishwasher"}',
                        call_id="search_1",
                    )
                ],
            ),
            SimpleNamespace(
                status="completed",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="propose_consumption",
                        arguments='{"item_id": 17, "amount": 2}',
                        call_id="proposal_1",
                    )
                ],
            ),
        ]
    )

    requests = []

    def fake_create(**kwargs):
        requests.append(kwargs)
        return next(fake_responses)

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(create=fake_create)
    )

    result = (
        proposal_orchestrator.prepare_agent_consumption_draft(
            original_request=(
                "I used two Classic dishwasher tablets."
            ),
            client=fake_client,
        )
    )

    assert result == {"status": "draft", "item_id": 17}
    assert read_calls == [
        ("search_items", '{"query": "dishwasher"}')
    ]
    assert len(requests) == 2

    assert any(
        tool["name"] == "search_items"
        for tool in requests[0]["tools"]
    )

    assert any(
        item.get("type") == "function_call_output"
        and item.get("call_id") == "search_1"
        for item in requests[1]["input"]
    )


def test_rejects_unsupported_model_tool():
    """The model cannot invent additional tool permissions."""

    fake_response = SimpleNamespace(
        status="completed",
        output=[
            SimpleNamespace(
                type="function_call",
                name="delete_item",
                arguments='{"item_id": 17}',
                call_id="unexpected_1",
            )
        ],
    )

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: fake_response
        )
    )

    with pytest.raises(
        ToolRequestError,
        match="Unsupported proposal tool",
    ):
        proposal_orchestrator.prepare_agent_consumption_draft(
            original_request=(
                "I used two Classic dishwasher tablets."
            ),
            client=fake_client,
        )


def test_rejects_multiple_model_tool_calls():
    """A response with multiple calls cannot produce a draft."""

    fake_response = SimpleNamespace(
        status="completed",
        output=[
            SimpleNamespace(
                type="function_call",
                name="propose_consumption",
                arguments='{"item_id": 17, "amount": 2}',
                call_id="proposal_1",
            ),
            SimpleNamespace(
                type="function_call",
                name="propose_consumption",
                arguments='{"item_id": 18, "amount": 2}',
                call_id="proposal_2",
            ),
        ],
    )

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: fake_response
        )
    )

    result = (
        proposal_orchestrator.prepare_agent_consumption_draft(
            original_request=(
                "I used two Classic dishwasher tablets."
            ),
            client=fake_client,
        )
    )

    assert result is None


def test_search_without_proposal_returns_none(monkeypatch):
    """Searching inventory does not require creating a draft."""

    monkeypatch.setattr(
        dispatcher,
        "dispatch_read_tool",
        lambda name, arguments_json: {
            "items": [],
            "has_more": False,
        },
    )

    fake_responses = iter(
        [
            SimpleNamespace(
                status="completed",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="search_items",
                        arguments='{"query": "dishwasher"}',
                        call_id="search_1",
                    )
                ],
            ),
            SimpleNamespace(
                status="completed",
                output=[
                    SimpleNamespace(
                        type="message",
                        content=[],
                    )
                ],
            ),
        ]
    )

    requests = []

    def fake_create(**kwargs):
        requests.append(kwargs)
        return next(fake_responses)

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(create=fake_create)
    )

    result = (
        proposal_orchestrator.prepare_agent_consumption_draft(
            original_request=(
                "I used two Classic dishwasher tablets."
            ),
            client=fake_client,
        )
    )

    assert result is None
    assert len(requests) == 2


def test_rejects_proposal_absent_from_search_results(
    monkeypatch,
):
    """A model cannot propose an item missing from its search evidence."""

    monkeypatch.setattr(
        dispatcher,
        "dispatch_read_tool",
        lambda name, arguments_json: {
            "items": [
                {
                    "id": 18,
                    "name": "Dishwasher tablets, Eco",
                }
            ],
            "has_more": False,
        },
    )

    draft_calls = []

    def fake_prepare_draft(original_request, arguments_json):
        draft_calls.append(arguments_json)
        return {"status": "draft", "item_id": 17}

    monkeypatch.setattr(
        proposal_orchestrator,
        "prepare_consumption_draft",
        fake_prepare_draft,
    )

    responses = iter(
        [
            SimpleNamespace(
                status="completed",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="search_items",
                        arguments='{"query": "dishwasher"}',
                        call_id="search_1",
                    )
                ],
            ),
            SimpleNamespace(
                status="completed",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="propose_consumption",
                        arguments='{"item_id": 17, "amount": 2}',
                        call_id="proposal_1",
                    )
                ],
            ),
        ]
    )

    client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: next(responses)
        )
    )

    with pytest.raises(
        ToolRequestError,
        match="not present in search results",
    ):
        proposal_orchestrator.prepare_agent_consumption_draft(
            original_request=(
                "I used two Classic dishwasher tablets."
            ),
            client=client,
        )

    assert draft_calls == []
