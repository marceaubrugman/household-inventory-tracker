from src.validators import normalize_text


def test_normalize_text_strips_spaces_and_capitalizes_first_letter():
    result = normalize_text("   kitchen cabinet   ")

    assert result == "Kitchen cabinet"


def test_normalize_text_normalizes_uppercase_input():
    result = normalize_text("PANTRY")

    assert result == "Pantry"