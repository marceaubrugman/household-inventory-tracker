import argparse
import json
from pathlib import Path

import psycopg

from src.database import get_connection


REQUIRED_FIELDS = {
    "id",
    "name",
    "category",
    "location",
    "quantity",
    "minimum_quantity",
}


class MigrationValidationError(ValueError):
    """Raised when JSON inventory data is invalid."""


def parse_arguments():
    """Return command-line arguments for the migration script."""

    parser = argparse.ArgumentParser(
        description=(
            "Migrate Household Inventory Tracker "
            "JSON data to PostgreSQL."
        )
    )

    parser.add_argument(
        "source",
        nargs="?",
        default="inventory.json",
        help=(
            "Path to the source JSON file. "
            "Defaults to inventory.json."
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the JSON data without writing to PostgreSQL.",
    )

    return parser.parse_args()


def load_json_items(file_path):
    """Load and return inventory records from a JSON file."""

    with file_path.open("r", encoding="utf-8") as source_file:
        return json.load(source_file)


def _validate_text_field(item, field, item_number):
    """Return a stripped, non-empty text field."""

    value = item.get(field)

    if not isinstance(value, str) or not value.strip():
        raise MigrationValidationError(
            f"Item {item_number}: "
            f"'{field}' must be non-empty text."
        )

    return value.strip()


def _validate_non_negative_integer(item, field, item_number):
    """Return a non-negative integer field."""

    value = item.get(field)

    if type(value) is not int or value < 0:
        raise MigrationValidationError(
            f"Item {item_number}: "
            f"'{field}' must be a non-negative integer."
        )

    return value


def validate_items(raw_items):
    """Validate and return migration-ready inventory records."""

    if not isinstance(raw_items, list):
        raise MigrationValidationError(
            "The JSON document must contain a list of items."
        )

    validated_items = []
    seen_ids = set()

    for item_number, item in enumerate(raw_items, start=1):
        if not isinstance(item, dict):
            raise MigrationValidationError(
                f"Item {item_number} must be a JSON object."
            )

        missing_fields = REQUIRED_FIELDS - item.keys()

        if missing_fields:
            missing_text = ", ".join(sorted(missing_fields))

            raise MigrationValidationError(
                f"Item {item_number} is missing: "
                f"{missing_text}."
            )

        item_id = item["id"]

        if type(item_id) is not int or item_id <= 0:
            raise MigrationValidationError(
                f"Item {item_number}: "
                "'id' must be a positive integer."
            )

        if item_id in seen_ids:
            raise MigrationValidationError(
                f"Item {item_number}: "
                f"duplicate ID {item_id}."
            )

        seen_ids.add(item_id)

        notes = item.get("notes", "")

        if not isinstance(notes, str):
            raise MigrationValidationError(
                f"Item {item_number}: "
                "'notes' must be text."
            )

        validated_items.append(
            {
                "id": item_id,
                "name": _validate_text_field(
                    item,
                    "name",
                    item_number,
                ),
                "category": _validate_text_field(
                    item,
                    "category",
                    item_number,
                ),
                "location": _validate_text_field(
                    item,
                    "location",
                    item_number,
                ),
                "quantity": _validate_non_negative_integer(
                    item,
                    "quantity",
                    item_number,
                ),
                "minimum_quantity": (
                    _validate_non_negative_integer(
                        item,
                        "minimum_quantity",
                        item_number,
                    )
                ),
                "notes": notes.strip(),
            }
        )

    return validated_items


def migrate_items(items):
    """Insert validated JSON items into an empty PostgreSQL table."""

    insert_query = """
        INSERT INTO hit.items (
            id,
            name,
            category,
            location,
            quantity,
            minimum_quantity,
            notes
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    parameters = [
        (
            item["id"],
            item["name"],
            item["category"],
            item["location"],
            item["quantity"],
            item["minimum_quantity"],
            item["notes"],
        )
        for item in items
    ]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database();"
            )
            database_result = cursor.fetchone()

            if database_result is None:
                raise RuntimeError(
                    "Could not determine the target database."
                )

            database_name = database_result[0]

            cursor.execute(
                "SELECT COUNT(*) FROM hit.items;"
            )
            count_result = cursor.fetchone()

            if count_result is None:
                raise RuntimeError(
                    "Could not inspect the target table."
                )

            existing_count = count_result[0]

            if existing_count != 0:
                raise RuntimeError(
                    "Migration refused: "
                    f"hit.items in '{database_name}' "
                    f"already contains {existing_count} item(s)."
                )

            cursor.executemany(
                insert_query,
                parameters,
            )

            cursor.execute(
                """
                SELECT setval(
                    pg_get_serial_sequence(
                        'hit.items',
                        'id'
                    ),
                    COALESCE(MAX(id), 1),
                    MAX(id) IS NOT NULL
                )
                FROM hit.items;
                """
            )

    return database_name, len(items)


def main():
    """Validate and optionally migrate JSON inventory data."""

    arguments = parse_arguments()
    source_path = Path(arguments.source)

    try:
        raw_items = load_json_items(source_path)
        validated_items = validate_items(raw_items)

        print(
            f"Validated {len(validated_items)} item(s) "
            f"from '{source_path}'."
        )

        if arguments.dry_run:
            print(
                "Dry run successful. "
                "No database changes were made."
            )
            return

        confirmation = input(
            "Type MIGRATE to write these items "
            "to PostgreSQL: "
        ).strip()

        if confirmation != "MIGRATE":
            print("Migration cancelled.")
            return

        database_name, migrated_count = migrate_items(
            validated_items
        )

        print(
            f"Migration successful: "
            f"{migrated_count} item(s) written "
            f"to '{database_name}'."
        )

    except FileNotFoundError:
        print(
            f"Migration failed: "
            f"'{source_path}' was not found."
        )
        raise SystemExit(1)

    except json.JSONDecodeError as error:
        print(
            "Migration failed: "
            f"invalid JSON near line {error.lineno}, "
            f"column {error.colno}."
        )
        raise SystemExit(1)

    except (
        MigrationValidationError,
        RuntimeError,
        psycopg.Error,
    ) as error:
        print(f"Migration failed: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()