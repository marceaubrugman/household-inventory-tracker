from psycopg.rows import dict_row

from src.database import get_connection


def get_all_items():
    query = """
        SELECT
            id,
            name,
            category,
            location,
            quantity,
            minimum_quantity,
            notes
        FROM hit.items
        ORDER BY LOWER(name), id;
    """

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query)
            return cursor.fetchall()