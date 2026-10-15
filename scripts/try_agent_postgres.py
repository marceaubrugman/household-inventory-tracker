
"""Run the read-only agent against local demo PostgreSQL."""

import os
from urllib.parse import urlsplit

from openai import OpenAI

from src.agent.orchestrator import answer_inventory_question
from src.database import get_database_url
from src.item_service import search_inventory_items


EXPECTED_ITEMS = {
    ("Dishwasher tablets, Classic", 24),
    ("Dishwasher tablets, Eco", 12),
}


def main() -> None:
    """Verify the demo database before calling the model."""

    database_url = get_database_url()

    if urlsplit(database_url).hostname != "db":
        raise RuntimeError(
            "Expected the local Docker database hostname 'db'."
        )

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    matches = search_inventory_items(
        "dishwasher tablets",
        limit=6,
    )

    actual_items = {
        (item["name"], item["quantity"])
        for item in matches
    }

    if (
        len(matches) != 2
        or actual_items != EXPECTED_ITEMS
    ):
        raise RuntimeError(
            "Demo database does not match expected test data."
        )

    print("Local PostgreSQL demo data verified: 2 items.")
    print("Starting read-only agent question...")
    print()

    client = OpenAI(
        timeout=20.0,
        max_retries=0,
    )

    answer = answer_inventory_question(
        "How many dishwasher tablets do we have?",
        client,
    )

    print("HIT ANSWER:")
    print(answer)


if __name__ == "__main__":
    main()
