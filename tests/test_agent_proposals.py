
from src.agent import proposals

import pytest


def test_build_consumption_proposal(monkeypatch):
    """Consumption produces a draft, not a database update."""

    def fake_find_inventory_item(item_id):
        assert item_id == 17

        return {
            "id": 17,
            "name": "Dishwasher tablets, Classic",
            "category": "Cleaning",
            "location": "Kitchen",
            "tracking_mode": "quantity",
            "quantity": 24,
            "minimum_quantity": 5,
            "notes": None,
        }

    monkeypatch.setattr(
        proposals,
        "find_inventory_item",
        fake_find_inventory_item,
    )

    result = proposals.build_consumption_proposal(
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
    "amount",
    [0, -1, True, 1.5],
)
def test_rejects_invalid_consumption_amount(
    monkeypatch,
    amount,
):
    """Only positive whole-number amounts are valid."""

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

    with pytest.raises(ValueError):
        proposals.build_consumption_proposal(
            item_id=17,
            amount=amount,
        )


def test_rejects_consumption_exceeding_stock(monkeypatch):
    """A proposal must never produce negative stock."""

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

    with pytest.raises(ValueError):
        proposals.build_consumption_proposal(
            item_id=17,
            amount=25,
        )



def test_rejects_missing_inventory_item(monkeypatch):
    """A missing item cannot produce a consumption proposal."""

    monkeypatch.setattr(
        proposals,
        "find_inventory_item",
        lambda item_id: None,
    )

    with pytest.raises(
        ValueError,
        match="Item not found",
    ):
        proposals.build_consumption_proposal(
            item_id=999,
            amount=2,
        )


def test_rejects_individual_tracked_item(monkeypatch):
    """Individually tracked items cannot be consumed by quantity."""

    monkeypatch.setattr(
        proposals,
        "find_inventory_item",
        lambda item_id: {
            "id": 18,
            "name": "Cordless drill",
            "tracking_mode": "individual",
            "quantity": None,
        },
    )

    with pytest.raises(
        ValueError,
        match="quantity-tracked",
    ):
        proposals.build_consumption_proposal(
            item_id=18,
            amount=1,
        )



@pytest.mark.parametrize(
    "item_id",
    [0, -1, True, "17", 1.5, None],
)
def test_rejects_invalid_item_id_before_lookup(
    monkeypatch,
    item_id,
):
    """Invalid IDs must be rejected before inventory lookup."""

    def unexpected_lookup(item_id):
        pytest.fail(
            "Invalid item ID reached inventory lookup."
        )

    monkeypatch.setattr(
        proposals,
        "find_inventory_item",
        unexpected_lookup,
    )

    with pytest.raises(
        ValueError,
        match="Item ID must be a positive integer",
    ):
        proposals.build_consumption_proposal(
            item_id=item_id,
            amount=2,
        )
