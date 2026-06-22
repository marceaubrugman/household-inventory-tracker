import os

import psycopg


class DatabaseConfigurationError(RuntimeError):
    """Raised when required database configuration is missing."""


def get_database_url():
    """Return the configured PostgreSQL URL."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise DatabaseConfigurationError(
            "DATABASE_URL is not configured."
        )

    return database_url


DATABASE_CONNECT_TIMEOUT = 5


def get_connection():
    """Open and return a PostgreSQL database connection."""

    return psycopg.connect(
        get_database_url(),
        connect_timeout=DATABASE_CONNECT_TIMEOUT,
    )