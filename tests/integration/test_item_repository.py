import psycopg
import pytest

from src.item_repository import (
    create_item,
    delete_item,
    get_all_items,
    get_item_by_id,
    get_low_stock_items,
    search_items,
    update_item,
)


pytestmark = pytest.mark.integration


def test_create_get_update_and_delete_item():
    """Verify the complete repository CRUD lifecycle."""

    created_item = create_item(
        name="Coffee filters",
        category="Food",
        location="Kitchen cabinet",
        quantity=2,
        minimum_quantity=1,
        notes="Size 4",
    )

    assert isinstance(created_item["id"], int)
    assert created_item["name"] == "Coffee filters"

    retrieved_item = get_item_by_id(created_item["id"])

    assert retrieved_item == created_item

    updated_item = update_item(
        item_id=created_item["id"],
        name="Coffee filters",
        category="Food",
        location="Pantry",
        quantity=5,
        minimum_quantity=2,
        notes="Size 4 filters",
    )

    assert updated_item is not None
    assert updated_item["location"] == "Pantry"
    assert updated_item["quantity"] == 5
    assert updated_item["minimum_quantity"] == 2

    deleted_item = delete_item(created_item["id"])

    assert deleted_item == updated_item
    assert get_item_by_id(created_item["id"]) is None


def test_searches_multiple_fields_and_sorts_numerically():
    """Verify multi-field search and numeric quantity sorting."""

    rice = create_item(
        name="Brown rice",
        category="Food",
        location="Pantry",
        quantity=10,
        minimum_quantity=3,
        notes="",
    )

    soap = create_item(
        name="Dish soap",
        category="Cleaning",
        location="Kitchen cabinet",
        quantity=2,
        minimum_quantity=1,
        notes="",
    )

    assert rice in search_items("rice")
    assert rice in search_items("food")
    assert rice in search_items("pantry")
    assert soap in search_items("SOAP")

    sorted_items = get_all_items("quantity")

    assert [
        item["quantity"] for item in sorted_items
    ] == [2, 10]


def test_returns_items_at_or_below_minimum_quantity():
    """Verify PostgreSQL applies the low-stock rule."""

    below_minimum = create_item(
        name="Toilet paper",
        category="Bathroom",
        location="Closet",
        quantity=1,
        minimum_quantity=4,
        notes="",
    )

    at_minimum = create_item(
        name="Dishwasher tablets",
        category="Cleaning",
        location="Kitchen",
        quantity=2,
        minimum_quantity=2,
        notes="",
    )

    above_minimum = create_item(
        name="Pasta",
        category="Food",
        location="Pantry",
        quantity=8,
        minimum_quantity=3,
        notes="",
    )

    low_stock_items = get_low_stock_items()
    low_stock_ids = {
        item["id"] for item in low_stock_items
    }

    assert below_minimum["id"] in low_stock_ids
    assert at_minimum["id"] in low_stock_ids
    assert above_minimum["id"] not in low_stock_ids


def test_database_rejects_negative_quantity():
    """Verify the database constraint rejects invalid stock."""

    with pytest.raises(psycopg.errors.CheckViolation):
        create_item(
            name="Invalid item",
            category="Testing",
            location="Laboratory",
            quantity=-1,
            minimum_quantity=0,
            notes="This must not be stored.",
        )

    assert get_all_items() == []