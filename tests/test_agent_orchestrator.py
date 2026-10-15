
from types import SimpleNamespace

import pytest

from src.agent import orchestrator
from src.agent.dispatcher import ToolRequestError


def fake_tool_call(name="search_items"):
    return SimpleNamespace(
        type="function_call",
        name=name,
        arguments='{"query": "dishwasher"}',
        call_id="call_123",
    )


def fake_response(output, answer=""):
    return SimpleNamespace(
        status="completed",
        output=output,
        output_text=answer,
    )


def test_agent_uses_tool_then_answers(monkeypatch):
    responses = iter([
        fake_response([fake_tool_call()]),
        fake_response(
            [],
            "You have 24 dishwasher tablets.",
        ),
    ])

    requests = []

    def fake_create(**kwargs):
        requests.append(kwargs)
        return next(responses)

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(create=fake_create)
    )

    def fake_dispatch(name, arguments):
        assert name == "search_items"
        return {
            "matches": [{
                "id": 17,
                "name": "Dishwasher tablets",
                "quantity": 24,
            }],
            "has_more": False,
        }

    monkeypatch.setattr(
        orchestrator,
        "dispatch_read_tool",
        fake_dispatch,
    )

    answer = orchestrator.answer_inventory_question(
        "How many dishwasher tablets?",
        fake_client,
    )

    assert answer == "You have 24 dishwasher tablets."
    assert len(requests) == 2
    assert requests[0]["tool_choice"] == "required"
    assert requests[1]["tool_choice"] == "auto"
    assert requests[0]["store"] is False
    assert requests[1]["input"][-1]["type"] == (
        "function_call_output"
    )
    assert '"quantity": 24' in (
        requests[1]["input"][-1]["output"]
    )


def test_agent_rejects_answer_without_tool():
    def fake_create(**kwargs):
        return fake_response(
            [],
            "You have 24 tablets.",
        )

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(create=fake_create)
    )

    with pytest.raises(
        RuntimeError,
        match="No inventory tool was used",
    ):
        orchestrator.answer_inventory_question(
            "How many tablets?",
            fake_client,
        )


def test_agent_rejects_unapproved_tool():
    def fake_create(**kwargs):
        return fake_response([
            fake_tool_call(name="delete_item")
        ])

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(create=fake_create)
    )

    with pytest.raises(ToolRequestError):
        orchestrator.answer_inventory_question(
            "Delete the dishwasher tablets",
            fake_client,
        )
