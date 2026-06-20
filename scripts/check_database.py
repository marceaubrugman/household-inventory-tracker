from src.database import get_connection


def main():
    query = """
        SELECT
            current_database(),
            current_user,
            to_regclass('hit.items');
    """

    with get_connection() as connection:
        result = connection.execute(query).fetchone()

    if result is None:
        raise RuntimeError("PostgreSQL returned no connection information.")

    database_name, user_name, items_table = result

    print("Database connection successful.")
    print(f"Database: {database_name}")
    print(f"User: {user_name}")
    print(f"Items table: {items_table or 'not found'}")

    if items_table is None:
        raise RuntimeError(
            "Connected successfully, but the hit.items table was not found."
        )


if __name__ == "__main__":
    main()