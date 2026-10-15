
"""Live agent experiment using synthetic inventory data."""

from openai import OpenAI

from src.agent import tools
from src.agent.orchestrator import answer_inventory_question


DEMO_ITEM = {
    "id": 17,
    "name": "Dishwasher tablets",
    "category": "Cleaning",
    "location": "Kitchen",
    "tracking_mode": "quantity",
    "quantity": 24,
    "minimum_quantity": 5,
    "notes": None,
}


def demo_search(
    search_term: str,
    sort_key: str = "name",
    limit: int | None = None,
    offset: int = 0,
) -> list[dict]:
    """Simulate the existing inventory search service."""
    print(f"[DEMO SERVICE] Searching for {search_term!r}")

    if search_term.casefold() in DEMO_ITEM["name"].casefold():
        matches = [DEMO_ITEM.copy()]
    else:
        matches = []

    if limit is None:
        return matches[offset:]

    return matches[offset:offset + limit]


def demo_find(item_id: int) -> dict | None:
    """Simulate retrieving one inventory item."""
    print(f"[DEMO SERVICE] Getting item ID {item_id}")

    if item_id == DEMO_ITEM["id"]:
        return DEMO_ITEM.copy()

    return None


def main() -> None:
    # Replace service functions only inside this demo process.
    tools.search_inventory_items = demo_search
    tools.find_inventory_item = demo_find

    client = OpenAI(
        timeout=20.0,
        max_retries=0,
    )

    print("HIT synthetic inventory experiment")
    print("No PostgreSQL connection will be used.")
    print()

    answer = answer_inventory_question(
        "How many dishwasher tablets do we have?",
        client,
    )

    print()
    print("HIT ANSWER:")
    print(answer)


if __name__ == "__main__":
    main()
