import os

import psycopg


def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Configure it before running the application."
        )

    return database_url


def get_connection():
    return psycopg.connect(get_database_url())