
from types import SimpleNamespace

import pytest

from src.agent import orchestrator
from src.agent.dispatcher import ToolRequestError

import psycopg


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



def test_missing_item_cannot_be_reported_as_zero(monkeypatch):
    """An empty search must not become a false zero-stock claim."""

    missing_item_call = SimpleNamespace(
        type="function_call",
        name="search_items",
        arguments='{"query": "coffee filters"}',
        call_id="call_missing",
    )

    responses = iter([
        fake_response([missing_item_call]),
        fake_response(
            [],
            "You have zero coffee filters.",
        ),
    ])

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: next(responses)
        )
    )

    def fake_dispatch(name, arguments):
        assert name == "search_items"
        return {
            "matches": [],
            "has_more": False,
        }

    monkeypatch.setattr(
        orchestrator,
        "dispatch_read_tool",
        fake_dispatch,
    )

    answer = orchestrator.answer_inventory_question(
        "How many coffee filters do we have?",
        fake_client,
    )

    assert answer == (
        "I couldn't find a matching item "
        "in the recorded inventory."
    )



def test_multiple_matches_cannot_silently_choose_one(monkeypatch):
    """The answer must not silently omit matching variations."""

    responses = iter([
        fake_response([fake_tool_call()]),
        fake_response(
            [],
            "You have 24 Classic dishwasher tablets.",
        ),
    ])

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: next(responses)
        )
    )

    def fake_dispatch(name, arguments):
        assert name == "search_items"

        return {
            "matches": [
                {
                    "id": 17,
                    "name": "Dishwasher tablets, Classic",
                    "tracking_mode": "quantity",
                    "quantity": 24,
                },
                {
                    "id": 18,
                    "name": "Dishwasher tablets, Eco",
                    "tracking_mode": "quantity",
                    "quantity": 12,
                },
            ],
            "has_more": False,
        }

    monkeypatch.setattr(
        orchestrator,
        "dispatch_read_tool",
        fake_dispatch,
    )

    answer = orchestrator.answer_inventory_question(
        "How many dishwasher tablets do we have?",
        fake_client,
    )

    assert "Dishwasher tablets, Classic" in answer
    assert "Dishwasher tablets, Eco" in answer
    assert "24" in answer
    assert "12" in answer



def test_truncated_search_warns_about_more_matches(monkeypatch):
    """Limited search results must not imply a complete inventory."""

    responses = iter([
        fake_response([fake_tool_call()]),
        fake_response(
            [],
            "There are exactly five dishwasher tablet variations.",
        ),
    ])

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: next(responses)
        )
    )

    def fake_dispatch(name, arguments):
        assert name == "search_items"

        return {
            "matches": [
                {
                    "id": number,
                    "name": f"Dishwasher tablets, Variant {number}",
                    "tracking_mode": "quantity",
                    "quantity": number,
                    "location": "Kitchen",
                }
                for number in range(1, 6)
            ],
            "has_more": True,
        }

    monkeypatch.setattr(
        orchestrator,
        "dispatch_read_tool",
        fake_dispatch,
    )

    answer = orchestrator.answer_inventory_question(
        "How many dishwasher tablet variations do we have?",
        fake_client,
    )

    for number in range(1, 6):
        assert (
            f"Dishwasher tablets, Variant {number}: "
            f"quantity {number}"
        ) in answer

    assert "More matches are available" in answer
    assert "exactly five" not in answer.lower()



def test_later_empty_search_preserves_earlier_matches(monkeypatch):
    """A later empty search must not erase earlier evidence."""

    first_call = SimpleNamespace(
        type="function_call",
        name="search_items",
        arguments='{"query": "dishwasher tablets"}',
        call_id="call_first",
    )

    second_call = SimpleNamespace(
        type="function_call",
        name="search_items",
        arguments='{"query": "dishwasher powder"}',
        call_id="call_second",
    )

    responses = iter([
        fake_response([first_call]),
        fake_response([second_call]),
        fake_response(
            [],
            "You have zero dishwasher tablets.",
        ),
    ])

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: next(responses)
        )
    )

    def fake_dispatch(name, arguments):
        assert name == "search_items"

        if arguments == first_call.arguments:
            return {
                "matches": [
                    {
                        "id": 17,
                        "name": "Dishwasher tablets, Classic",
                        "tracking_mode": "quantity",
                        "quantity": 24,
                    },
                    {
                        "id": 18,
                        "name": "Dishwasher tablets, Eco",
                        "tracking_mode": "quantity",
                        "quantity": 12,
                    },
                ],
                "has_more": False,
            }

        if arguments == second_call.arguments:
            return {
                "matches": [],
                "has_more": False,
            }

        raise AssertionError("Unexpected tool arguments")

    monkeypatch.setattr(
        orchestrator,
        "dispatch_read_tool",
        fake_dispatch,
    )

    answer = orchestrator.answer_inventory_question(
        "How many dishwasher tablets do we have?",
        fake_client,
    )

    assert "Dishwasher tablets, Classic" in answer
    assert "Dishwasher tablets, Eco" in answer
    assert "24" in answer
    assert "12" in answer



def test_agent_database_outage_has_safe_error(monkeypatch):
    """Database failures should not expose connection details."""

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **kwargs: fake_response([
                fake_tool_call()
            ])
        )
    )

    def unavailable_database(name, arguments):
        raise psycopg.OperationalError(
            "Sensitive database connection details"
        )

    monkeypatch.setattr(
        orchestrator,
        "dispatch_read_tool",
        unavailable_database,
    )

    with pytest.raises(
        RuntimeError,
        match="Inventory data is temporarily unavailable.",
    ) as error_info:
        orchestrator.answer_inventory_question(
            "How many dishwasher tablets do we have?",
            fake_client,
        )

    assert "Sensitive database" not in str(
        error_info.value
    )
