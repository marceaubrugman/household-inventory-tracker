from psycopg.rows import dict_row

from src.database import get_connection


def _escape_like_pattern(value):
    return (
        value
        .replace("!", "!!")
        .replace("%", "!%")
        .replace("_", "!_")
    )


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


def get_item_by_id(item_id):
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
        WHERE id = %s;
    """

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (item_id,))
            return cursor.fetchone()


def search_items(search_term):
    normalized_term = search_term.strip()

    if not normalized_term:
        return []

    escaped_term = _escape_like_pattern(normalized_term)
    pattern = f"%{escaped_term}%"

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
        WHERE name ILIKE %s ESCAPE '!'
           OR category ILIKE %s ESCAPE '!'
           OR location ILIKE %s ESCAPE '!'
        ORDER BY LOWER(name), id;
    """

    parameters = (pattern, pattern, pattern)

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, parameters)
            return cursor.fetchall()