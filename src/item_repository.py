from psycopg import sql
from psycopg.rows import dict_row

from src.database import get_connection


SORT_EXPRESSIONS = {
    "name": sql.SQL("LOWER(name)"),
    "category": sql.SQL("LOWER(category)"),
    "location": sql.SQL("LOWER(location)"),
    "quantity": sql.Identifier("quantity"),
}


def _escape_like_pattern(value):
    """Escape SQL LIKE wildcard characters in a search value."""
    return (
        value
        .replace("!", "!!")
        .replace("%", "!%")
        .replace("_", "!_")
    )


def _get_sort_expression(sort_key):
    """Return an approved SQL sort expression."""
    try:
        return SORT_EXPRESSIONS[sort_key]
    except KeyError as error:
        raise ValueError(
            f"Unsupported sort key: {sort_key}"
        ) from error


def create_item(
    name,
    category,
    location,
    quantity,
    minimum_quantity,
    notes="",
):
    """Insert an inventory item and return the created row."""
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


def get_all_items(sort_key="name"):
    """Return all inventory items in the requested sort order."""
    sort_expression = _get_sort_expression(sort_key)

    query = sql.SQL(
        """
        SELECT
            id,
            name,
            category,
            location,
            quantity,
            minimum_quantity,
            notes
        FROM hit.items
        ORDER BY {sort_expression}, id;
        """
    ).format(
        sort_expression=sort_expression
    )

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_item_by_id(item_id):
    """Return one inventory item by ID, or None if absent."""
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
    """Return items matching a literal case-insensitive search term."""
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


def update_item(
    item_id,
    name,
    category,
    location,
    quantity,
    minimum_quantity,
    notes,
):
    """Update an inventory item and return the changed row."""
    query = """
        UPDATE hit.items
        SET
            name = %s,
            category = %s,
            location = %s,
            quantity = %s,
            minimum_quantity = %s,
            notes = %s
        WHERE id = %s
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
        item_id,
    )

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, parameters)
            return cursor.fetchone()


def delete_item(item_id):
    """Delete an inventory item and return the removed row."""
    query = """
        DELETE FROM hit.items
        WHERE id = %s
        RETURNING
            id,
            name,
            category,
            location,
            quantity,
            minimum_quantity,
            notes;
    """

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (item_id,))
            return cursor.fetchone()


def get_low_stock_items(sort_key="name"):
    """Return items at or below their minimum quantity."""
    sort_expression = _get_sort_expression(sort_key)

    query = sql.SQL(
        """
        SELECT
            id,
            name,
            category,
            location,
            quantity,
            minimum_quantity,
            notes
        FROM hit.items
        WHERE quantity <= minimum_quantity
        ORDER BY {sort_expression}, id;
        """
    ).format(
        sort_expression=sort_expression
    )

    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query)
            return cursor.fetchall()