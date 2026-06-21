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

def create_item(
    name,
    category,
    location,
    quantity,
    minimum_quantity,
    notes="",
):
    query = """
        INSERT INTO hit.items (
            name,
            category,
            location,
            quantity,
            minimum_quantity,
            notes
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING
            id,
            name,
            category,
            location,
            quantity,
            minimum_quantity,
            notes;
    """

    parameters = (
        name,
        category,
        location,
        quantity,
        minimum_quantity,
        notes,
    )

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, parameters)
            created_item = cursor.fetchone()

    if created_item is None:
        raise RuntimeError("PostgreSQL did not return the created item.")

    return created_item