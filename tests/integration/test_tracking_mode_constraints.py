import os

import psycopg
import pytest


pytestmark = pytest.mark.integration


def test_database_accepts_individual_item_without_quantities():
    """Verify individual assets do not require stock quantities."""
    test_database_url = os.environ["TEST_DATABASE_URL"]

    with psycopg.connect(test_database_url) as connection:
        created_item = connection.execute(
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
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING
                tracking_mode,
                quantity,
                minimum_quantity;
            """,
            (
                "Cordless drill",
                "Tools",
                "Garage",
                "individual",
                None,
                None,
                "Blue carrying case",
            ),
        ).fetchone()

    assert created_item == (
        "individual",
        None,
        None,
    )


@pytest.mark.parametrize(
    (
        "tracking_mode",
        "quantity",
        "minimum_quantity",
    ),
    [
        ("quantity", None, None),
        ("quantity", 1, None),
        ("individual", 1, 0),
        ("individual", None, 0),
    ],
)
def test_database_rejects_quantities_that_do_not_match_mode(
    tracking_mode,
    quantity,
    minimum_quantity,
):
    """Verify quantity fields match the selected tracking mode."""
    test_database_url = os.environ["TEST_DATABASE_URL"]

    with pytest.raises(psycopg.errors.CheckViolation):
        with psycopg.connect(test_database_url) as connection:
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
                    "Invalid combination",
                    "Testing",
                    "Laboratory",
                    tracking_mode,
                    quantity,
                    minimum_quantity,
                    "",
                ),
            )
