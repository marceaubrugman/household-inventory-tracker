
import pytest

from src.agent import resolver


ITEMS = [
    {
        "id": 17,
        "name": "Dishwasher tablets, Classic",
    },
    {
        "id": 18,
        "name": "Dishwasher tablets, Eco",
    },
]


@pytest.mark.parametrize(
    "original_request, expected_id",
    [
        (
            "I used two Classic dishwasher tablets.",
            17,
        ),
        (
            "I used two dishwasher tablets.",
            None,
        ),
    ],
)
def test_resolves_item_from_original_request(
    monkeypatch,
    original_request,
    expected_id,
):
    """Resolve only when the user's wording supports one item."""

    def fake_list_inventory_items(
        sort_key="name",
        limit=None,
        offset=0,
    ):
        assert sort_key == "name"
        assert limit == resolver.MAX_RESOLUTION_ITEMS + 1
        assert offset == 0
        return ITEMS

    monkeypatch.setattr(
        resolver,
        "list_inventory_items",
        fake_list_inventory_items,
    )

    result = resolver.resolve_consumption_item(
        original_request
    )

    assert result == expected_id


def test_rejects_incomplete_inventory_snapshot(monkeypatch):
    """Never resolve identity from a truncated inventory snapshot."""

    items = [
        {
            "id": 17,
            "name": "Dishwasher tablets, Classic",
        }
    ]

    items.extend(
        {
            "id": 100 + index,
            "name": f"Unrelated item {index}",
        }
        for index in range(resolver.MAX_RESOLUTION_ITEMS)
    )

    def fake_list_inventory_items(
        sort_key="name",
        limit=None,
        offset=0,
    ):
        assert sort_key == "name"
        assert limit == resolver.MAX_RESOLUTION_ITEMS + 1
        assert offset == 0
        return items

    monkeypatch.setattr(
        resolver,
        "list_inventory_items",
        fake_list_inventory_items,
    )

    assert resolver.resolve_consumption_item(
        "I used two Classic dishwasher tablets."
    ) is None


@pytest.mark.parametrize(
    "items",
    [
        [
            {"id": 17, "name": "Dishwasher tablets, Classic"},
            {"id": 19, "name": "Dishwasher tablets, Classic"},
        ],
        [
            {"id": 17, "name": "Dishwasher tablets, Classic"},
            {"id": 19, "name": "Dishwasher tablets"},
        ],
    ],
)
def test_rejects_multiple_matching_inventory_names(
    monkeypatch,
    items,
):
    """Multiple matching records require clarification."""

    monkeypatch.setattr(
        resolver,
        "list_inventory_items",
        lambda **kwargs: items,
    )

    assert resolver.resolve_consumption_item(
        "I used two Classic dishwasher tablets."
    ) is None
