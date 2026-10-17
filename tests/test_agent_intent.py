
import pytest

from src.agent import intent


@pytest.mark.parametrize(
    "original_request, expected_amount",
    [
        (
            "I used two Classic dishwasher tablets.",
            2,
        ),
        (
            "I used 2 Classic dishwasher tablets.",
            2,
        ),
        (
            "I didn't use any Classic dishwasher tablets.",
            None,
        ),
        (
            "I bought two Classic dishwasher tablets.",
            None,
        ),
        (
            "If I used two Classic dishwasher tablets, "
            "what would remain?",
            None,
        ),
        (
            "I used to buy two Classic dishwasher tablets.",
            None,
        ),
    ],
)
def test_resolves_explicit_consumption_intent(
    original_request,
    expected_amount,
):
    """Only supported, affirmative consumption requests qualify."""

    assert intent.resolve_consumption_amount(
        original_request
    ) == expected_amount


@pytest.mark.parametrize(
    "original_request",
    [
        "I used two Classic dishwasher tablets, maybe.",
        "I used two Classic dishwasher tablets, I think.",
        "I used two Classic dishwasher tablets, just kidding.",
    ],
)
def test_rejects_uncertain_consumption_statements(
    original_request,
):
    """Uncertain statements must not produce consumption amounts."""

    assert intent.resolve_consumption_amount(
        original_request
    ) is None
