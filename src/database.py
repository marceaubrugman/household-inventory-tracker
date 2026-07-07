import os

import psycopg


class DatabaseConfigurationError(RuntimeError):
    """Raised when required database configuration is missing."""


DATABASE_CONNECT_TIMEOUT = 5


def get_database_url() -> str:
    """Return the configured PostgreSQL URL."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise DatabaseConfigurationError(
            "DATABASE_URL is not configured."
        )

    return database_url


def get_connection() -> psycopg.Connection:
    """Open and return a PostgreSQL database connection."""
    return psycopg.connect(
        get_database_url(),
        connect_timeout=DATABASE_CONNECT_TIMEOUT,
    )


def check_database_connection() -> dict[str, str]:
    """Check whether the application can connect to PostgreSQL."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database(), current_user;")
            database_name, database_user = cursor.fetchone()

    return {
        "database": database_name,
        "user": database_user,
    }