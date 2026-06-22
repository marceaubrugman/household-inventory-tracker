import os

import psycopg
import pytest


def _clean_test_database(database_url):
    """Remove all test items and reset generated item IDs."""

    with psycopg.connect(
        database_url,
        connect_timeout=5,
    ) as connection:
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
                "Refusing to clean a database whose name "
                "does not end with '_test'."
            )

        connection.execute(
            "TRUNCATE TABLE hit.items RESTART IDENTITY;"
        )


@pytest.fixture(autouse=True)
def isolated_test_database(monkeypatch):
    """Route each integration test to a clean test database."""

    test_database_url = os.getenv("TEST_DATABASE_URL")

    if not test_database_url:
        pytest.skip(
            "TEST_DATABASE_URL is not configured."
        )

    monkeypatch.setenv(
        "DATABASE_URL",
        test_database_url,
    )

    _clean_test_database(test_database_url)

    yield

    _clean_test_database(test_database_url)