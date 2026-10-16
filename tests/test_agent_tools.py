
import pytest
from pydantic import ValidationError

from src.agent import proposals, tools


def test_search_items_returns_matching_inventory(monkeypatch):
    """The tool should reuse the existing inventory service."""

    def fake_search(search_term, sort_key, limit, offset):
        assert search_term == "dishwasher"
        assert sort_key == "name"
        assert limit == 6
        assert offset == 0

        return [{
            "id": 17,
            "name": "Dishwasher tablets",
            "category": "Cleaning",
            "location": "Kitchen",
            "tracking_mode": "quantity",
            "quantity": 24,
            "minimum_quantity": 5,
            "notes": "Private household note",
        }]

    monkeypatch.setattr(
        tools,
        "search_inventory_items",
        fake_search,
    )

    result = tools.search_items("  dishwasher  ")

    assert result == {
        "matches": [{
            "id": 17,
            "name": "Dishwasher tablets",
            "category": "Cleaning",
            "location": "Kitchen",
            "tracking_mode": "quantity",
            "quantity": 24,
        }],
        "has_more": False,
    }


@pytest.mark.parametrize("query", ["", "   ", "x" * 101])
def test_search_items_rejects_invalid_input(query):
    with pytest.raises(ValidationError):
        tools.search_items(query)


def test_search_items_limits_results(monkeypatch):
    def fake_search(search_term, sort_key, limit, offset):
        return [{
            "id": number,
            "name": f"Item {number}",
            "category": "Test",
            "location": "Shelf",
            "tracking_mode": "quantity",
            "quantity": 1,
        } for number in range(1, 7)]

    monkeypatch.setattr(
        tools,
        "search_inventory_items",
        fake_search,
    )

    result = tools.search_items("item")

    assert len(result["matches"]) == 5
    assert result["has_more"] is True



def test_get_item_returns_existing_item(monkeypatch):
    def fake_find(item_id):
        assert item_id == 17
        return {
            "id": 17,
            "name": "Dishwasher tablets",
            "category": "Cleaning",
            "location": "Kitchen",
            "tracking_mode": "quantity",
            "quantity": 24,
            "minimum_quantity": 5,
            "notes": "Private note",
        }

    monkeypatch.setattr(
        tools,
        "find_inventory_item",
        fake_find,
    )

    result = tools.get_item(17)

    assert result["status"] == "found"
    assert result["item"]["quantity"] == 24
    assert result["item"]["minimum_quantity"] == 5
    assert "notes" not in result["item"]


def test_get_item_handles_missing_item(monkeypatch):
    monkeypatch.setattr(
        tools,
        "find_inventory_item",
        lambda item_id: None,
    )

    assert tools.get_item(999) == {
        "status": "not_found",
        "item": None,
    }


def test_get_item_handles_individual_tracking(monkeypatch):
    def fake_find(item_id):
        return {
            "id": 2,
            "name": "Cordless drill",
            "category": "Tools",
            "location": "Garage",
            "tracking_mode": "individual",
            "quantity": None,
            "minimum_quantity": None,
        }

    monkeypatch.setattr(
        tools,
        "find_inventory_item",
        fake_find,
    )

    result = tools.get_item(2)

    assert result["status"] == "found"
    assert result["item"]["quantity"] is None


@pytest.mark.parametrize(
    "item_id",
    [0, -1, "17", True],
)
def test_get_item_rejects_invalid_ids(item_id):
    with pytest.raises(ValidationError):
        tools.get_item(item_id)


def test_propose_consumption_tool_returns_draft(monkeypatch):
    """The proposal tool delegates to read-only domain logic."""

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

    result = tools.propose_consumption(
        item_id=17,
        amount=2,
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



@pytest.mark.parametrize(
    "item_id, amount",
    [
        (0, 2),
        (-1, 2),
        (True, 2),
        ("17", 2),
        (1.5, 2),
        (17, 0),
        (17, -1),
        (17, True),
        (17, "2"),
        (17, 1.5),
    ],
)
def test_proposal_tool_rejects_invalid_arguments(
    monkeypatch,
    item_id,
    amount,
):
    """Invalid tool inputs must never reach proposal logic."""

    def unexpected_proposal(**kwargs):
        pytest.fail(
            "Invalid arguments reached proposal builder."
        )

    monkeypatch.setattr(
        proposals,
        "build_consumption_proposal",
        unexpected_proposal,
    )

    with pytest.raises(ValidationError):
        tools.propose_consumption(
            item_id=item_id,
            amount=amount,
        )


def test_proposal_tool_rejects_unexpected_fields():
    """The tool input contract must forbid extra arguments."""

    with pytest.raises(ValidationError):
        tools.ProposeConsumptionInput.model_validate(
            {
                "item_id": 17,
                "amount": 2,
                "approved": True,
            }
        )
