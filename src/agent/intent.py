
"""Recognize explicitly supported consumption requests."""

import re


NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


CONSUMPTION_PATTERN = re.compile(
    r"i used "
    r"(?P<amount>[1-9][0-9]*|one|two|three|four|five|six|"
    r"seven|eight|nine|ten) "
    r"(?P<item>[a-z][a-z0-9 '-]*)\.?",
    re.IGNORECASE,
)


def resolve_consumption_amount(
    original_request: str,
) -> int | None:
    """Recognize a simple affirmative consumption statement."""

    if not isinstance(original_request, str):
        return None

    match = CONSUMPTION_PATTERN.fullmatch(
        original_request.strip()
    )

    if match is None:
        return None

    item_description = match.group("item").casefold()

    # Reject common markers of negation or additional clauses.
    if re.search(
        r"\b(?:but|not|never|instead|actually|or|and|"
        r"if|would|didn't|don't)\b",
        item_description,
    ):
        return None

    amount_text = match.group("amount").casefold()

    if amount_text in NUMBER_WORDS:
        return NUMBER_WORDS[amount_text]

    return int(amount_text)
