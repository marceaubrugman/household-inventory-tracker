from src.inventory_service import (
    find_item_by_id,
    get_low_stock_items,
    get_next_id,
    search_items,
    sort_items,
)


def sample_items():
    return [
        {
            "id": 1,
            "name": "Rice",
            "category": "Food",
            "location": "Pantry",
            "quantity": 2,
            "minimum_quantity": 3,
            "notes": "",
        },
        {
            "id": 2,
            "name": "Dish Soap",
            "category": "Cleaning",
            "location": "Kitchen Cabinet",
            "quantity": 1,
            "minimum_quantity": 1,
            "notes": "",
        },
        {
            "id": 3,
            "name": "Toilet Paper",
            "category": "Bathroom",
            "location": "Upstairs Closet",
            "quantity": 6,
            "minimum_quantity": 4,
            "notes": "",
        },
    ]


def test_sort_items_sorts_quantity_numerically():
    items = [
        {
            "id": 1,
            "name": "Rice",
            "category": "Food",
            "location": "Pantry",
            "quantity": 10,
            "minimum_quantity": 2,
            "notes": "",
        },
        {
            "id": 2,
            "name": "Pasta",
            "category": "Food",
            "location": "Pantry",
            "quantity": 2,
            "minimum_quantity": 1,
            "notes": "",
        },
        {
            "id": 3,
            "name": "Soap",
            "category": "Cleaning",
            "location": "Cupboard",
            "quantity": 1,
            "minimum_quantity": 1,
            "notes": "",
        },
    ]

    results = sort_items(items, "quantity")
    quantities = [item["quantity"] for item in results]

    assert quantities == [1, 2, 10]


def test_get_next_id_returns_1_for_empty_list():
    assert get_next_id([]) == 1


def test_get_next_id_returns_next_highest_id():
    items = sample_items()
    assert get_next_id(items) == 4


def test_search_items_finds_partial_case_insensitive_match():
    items = sample_items()
    results = search_items(items, "soap")

    assert len(results) == 1
    assert results[0]["name"] == "Dish Soap"


def test_search_items_returns_empty_list_when_no_match():
    items = sample_items()
    results = search_items(items, "coffee")

    assert results == []


def test_find_item_by_id_returns_matching_item():
    items = sample_items()
    item = find_item_by_id(items, 2)

    assert item is not None
    assert item["name"] == "Dish Soap"


def test_find_item_by_id_returns_none_when_missing():
    items = sample_items()
    item = find_item_by_id(items, 99)

    assert item is None


def test_get_low_stock_items_returns_items_at_or_below_minimum():
    items = sample_items()
    results = get_low_stock_items(items)

    names = [item["name"] for item in results]

    assert "Rice" in names
    assert "Dish Soap" in names
    assert "Toilet Paper" not in names


def test_search_items_with_empty_string_returns_all_items():
    items = sample_items()
    results = search_items(items, "")

    assert len(results) == len(items)


def test_get_low_stock_items_returns_empty_list_when_all_items_are_above_minimum():
    items = [
        {
            "id": 1,
            "name": "Pasta",
            "category": "Food",
            "location": "Pantry",
            "quantity": 5,
            "minimum_quantity": 2,
            "notes": "",
        },
        {
            "id": 2,
            "name": "Shampoo",
            "category": "Bathroom",
            "location": "Bathroom Cabinet",
            "quantity": 3,
            "minimum_quantity": 1,
            "notes": "",
        },
    ]

    results = get_low_stock_items(items)

    assert results == []

def test_search_items_finds_category_match():
    items = sample_items()

    results = search_items(items, "cleaning")

    assert len(results) == 1
    assert results[0]["name"] == "Dish Soap"


def test_search_items_finds_location_match_case_insensitively():
    items = sample_items()

    results = search_items(items, "UPSTAIRS CLOSET")

    assert len(results) == 1
    assert results[0]["name"] == "Toilet Paper"