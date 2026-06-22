import pytest

from scripts.migrate_json_to_postgres import (
    MigrationValidationError,
    validate_items,
)


def make_valid_item(**changes):
    """Return valid migration data with optional field changes."""

    item = {
        "id": 1,
        "name": "Rice",
        "category": "Food",
        "location": "Pantry",
        "quantity": 2,
        "minimum_quantity": 3,
        "notes": "",
    }

    item.update(changes)
    return item


def test_validate_items_returns_clean_records():
    """Verify valid records are cleaned and returned."""

    raw_items = [
        make_valid_item(
            name="  Rice  ",
            category="  Food  ",
            location="  Pantry  ",
            notes="  Buy soon  ",
        )
    ]

    validated_items = validate_items(raw_items)

    assert validated_items == [
        {
            "id": 1,
            "name": "Rice",
            "category": "Food",
            "location": "Pantry",
            "quantity": 2,
            "minimum_quantity": 3,
            "notes": "Buy soon",
        }
    ]


def test_validate_items_adds_empty_notes_when_absent():
    """Verify notes default to an empty string."""

    item = make_valid_item()
    del item["notes"]

    validated_items = validate_items([item])

    assert validated_items[0]["notes"] == ""


def test_validate_items_rejects_duplicate_ids():
    """Verify duplicate source IDs are rejected."""

    raw_items = [
        make_valid_item(id=1),
        make_valid_item(id=1, name="Pasta"),
    ]

    with pytest.raises(
        MigrationValidationError,
        match="duplicate ID 1",
    ):
        validate_items(raw_items)


def test_validate_items_rejects_missing_required_field():
    """Verify required migration fields cannot be omitted."""

    item = make_valid_item()
    del item["location"]

    with pytest.raises(
        MigrationValidationError,
        match="location",
    ):
        validate_items([item])


def test_validate_items_rejects_negative_quantity():
    """Verify negative stock values are rejected."""

    with pytest.raises(
        MigrationValidationError,
        match="quantity",
    ):
        validate_items(
            [make_valid_item(quantity=-1)]
        )


def test_validate_items_rejects_non_list_document():
    """Verify the JSON root must be a list."""

    with pytest.raises(
        MigrationValidationError,
        match="list of items",
    ):
        validate_items(
            {"id": 1, "name": "Rice"}
        )