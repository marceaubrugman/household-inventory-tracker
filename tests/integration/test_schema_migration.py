import os
from pathlib import Path

import psycopg
import pytest


pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[2]

V0_5_0_SCHEMA_PATH = (
    PROJECT_ROOT
    / "tests"
    / "integration"
    / "fixtures"
    / "schema_v0_5_0.sql"
)

MIGRATION_PATH = (
    PROJECT_ROOT
    / "sql"
    / "migrations"
    / "001_add_tracking_mode.sql"
)

CURRENT_SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


def _read_sql(file_path: Path) -> str:
    """Return the SQL stored in a repository file."""
    return file_path.read_text(encoding="utf-8")


def _require_test_database(
    connection: psycopg.Connection,
) -> None:
    """Refuse destructive schema work outside a test database."""
    result = connection.execute(
        "SELECT current_database();"
    ).fetchone()

    if result is None:
        raise RuntimeError(
            "Could not determine the connected database."
        )

    database_name = result[0]

    if not database_name.endswith("_test"):
        raise RuntimeError(
            "Refusing schema migration testing against "
            "a database whose name does not end with '_test'."
        )


def _replace_hit_schema(
    connection: psycopg.Connection,
    schema_sql: str,
) -> None:
    """Replace the HIT schema with a known schema definition."""
    connection.execute("DROP SCHEMA IF EXISTS hit CASCADE;")
    connection.execute(schema_sql)


def test_tracking_mode_migration_upgrades_v0_5_0_schema():
    """Verify the v0.5.0 schema upgrades without data loss."""
    test_database_url = os.environ["TEST_DATABASE_URL"]

    old_schema_sql = _read_sql(V0_5_0_SCHEMA_PATH)
    migration_sql = _read_sql(MIGRATION_PATH)
    current_schema_sql = _read_sql(CURRENT_SCHEMA_PATH)

    with psycopg.connect(
        test_database_url,
        autocommit=True,
    ) as connection:
        _require_test_database(connection)

        try:
            _replace_hit_schema(
                connection,
                old_schema_sql,
            )

            old_item = connection.execute(
                """
                INSERT INTO hit.items (
                    name,
                    category,
                    location,
                    quantity,
                    minimum_quantity,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    "Brown rice",
                    "Food",
                    "Pantry",
                    10,
                    3,
                    "Existing v0.5.0 record",
                ),
            ).fetchone()

            assert old_item is not None
            old_item_id = old_item[0]

            connection.execute(migration_sql)

            migrated_item = connection.execute(
                """
                SELECT
                    name,
                    category,
                    location,
                    quantity,
                    minimum_quantity,
                    notes,
                    tracking_mode
                FROM hit.items
                WHERE id = %s;
                """,
                (old_item_id,),
            ).fetchone()

            assert migrated_item == (
                "Brown rice",
                "Food",
                "Pantry",
                10,
                3,
                "Existing v0.5.0 record",
                "quantity",
            )

            default_mode = connection.execute(
                """
                INSERT INTO hit.items (
                    name,
                    category,
                    location,
                    quantity,
                    minimum_quantity,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING tracking_mode;
                """,
                (
                    "Dish soap",
                    "Cleaning",
                    "Kitchen",
                    2,
                    1,
                    "",
                ),
            ).fetchone()

            assert default_mode == ("quantity",)

            with pytest.raises(
                psycopg.errors.CheckViolation
            ):
                connection.execute(
                    """
                    INSERT INTO hit.items (
                        name,
                        category,
                        location,
                        tracking_mode,
                        quantity,
                        minimum_quantity,
                        notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        "Invalid item",
                        "Testing",
                        "Laboratory",
                        "unsupported",
                        1,
                        0,
                        "",
                    ),
                )

            with pytest.raises(
                psycopg.errors.NotNullViolation
            ):
                connection.execute(
                    """
                    INSERT INTO hit.items (
                        name,
                        category,
                        location,
                        tracking_mode,
                        quantity,
                        minimum_quantity,
                        notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        "Null mode",
                        "Testing",
                        "Laboratory",
                        None,
                        1,
                        0,
                        "",
                    ),
                )

            with pytest.raises(
                psycopg.errors.DuplicateColumn
            ):
                connection.execute(migration_sql)

            connection.rollback()

        finally:
            _replace_hit_schema(
                connection,
                current_schema_sql,
            )
