
from src.agent import proposals, resolver, workflow

import pytest

from src.agent.dispatcher import ToolRequestError

def test_prepares_guarded_consumption_draft(monkeypatch):
    """Verified intent and item identity produce a draft."""

    inventory = [
        {
            "id": 17,
            "name": "Dishwasher tablets, Classic",
        },
        {
            "id": 18,
            "name": "Dishwasher tablets, Eco",
        },
    ]

    monkeypatch.setattr(
        resolver,
        "list_inventory_items",
        lambda **kwargs: inventory,
    )

    def fake_find_inventory_item(item_id):
        assert item_id == 17

        return {
            "id": 17,
            "name": "Dishwasher tablets, Classic",
            "tracking_mode": "quantity",
            "quantity": 24,
        }

    monkeypatch.setattr(
        proposals,
        "find_inventory_item",
        fake_find_inventory_item,
    )

    result = workflow.prepare_consumption_draft(
        original_request=(
            "I used two Classic dishwasher tablets."
        ),
        arguments_json='{"item_id": 17, "amount": 2}',
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


@pytest.fixture
def known_inventory(monkeypatch):
    """Provide two fictional products without PostgreSQL."""

    items = [
        {
            "id": 17,
            "name": "Dishwasher tablets, Classic",
        },
        {
            "id": 18,
            "name": "Dishwasher tablets, Eco",
        },
    ]

    monkeypatch.setattr(
        resolver,
        "list_inventory_items",
        lambda **kwargs: items,
    )

    def fake_find_inventory_item(item_id):
        assert item_id == 17

        return {
            "id": 17,
            "name": "Dishwasher tablets, Classic",
            "tracking_mode": "quantity",
            "quantity": 24,
        }

    monkeypatch.setattr(
        proposals,
        "find_inventory_item",
        fake_find_inventory_item,
    )


@pytest.mark.parametrize(
    "arguments_json, expected_error",
    [
        (
            '{"item_id": 18, "amount": 2}',
            "Proposed item does not match resolved item",
        ),
        (
            '{"item_id": 17, "amount": 5}',
            "Proposed amount does not match resolved consumption",
        ),
        (
            '{"item_id": 17, "amount": 2, "approved": true}',
            "Invalid tool arguments",
        ),
    ],
)
def test_rejects_untrusted_model_arguments(
    known_inventory,
    arguments_json,
    expected_error,
):
    """Model arguments cannot override verified user evidence."""

    with pytest.raises(
        ToolRequestError,
        match=expected_error,
    ):
        workflow.prepare_consumption_draft(
            original_request=(
                "I used two Classic dishwasher tablets."
            ),
            arguments_json=arguments_json,
        )


@pytest.mark.parametrize(
    "original_request",
    [
        "I used two dishwasher tablets.",
        (
            "If I used two Classic dishwasher tablets, "
            "what would remain?"
        ),
        "I bought two Classic dishwasher tablets.",
    ],
)
def test_returns_no_draft_without_user_evidence(
    known_inventory,
    original_request,
):
    """Ambiguous or unsupported requests cannot produce drafts."""

    result = workflow.prepare_consumption_draft(
        original_request=original_request,
        arguments_json='{"item_id": 17, "amount": 2}',
    )

    assert result is None


@pytest.mark.parametrize(
    "original_request",
    [
        "I used two Classic dishwasher tablets maybe.",
        "I used two Classic dishwasher tablets I think.",
        "I used two Classic dishwasher tablets just kidding.",
    ],
)
def test_rejects_unverified_trailing_language(
    known_inventory,
    original_request,
):
    """Extra language must not silently become product identity."""

    result = workflow.prepare_consumption_draft(
        original_request=original_request,
        arguments_json='{"item_id": 17, "amount": 2}',
    )

    assert result is None
