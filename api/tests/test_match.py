import pytest

from app.services.match import match_item, normalise_item_name
from app.services.reference import ReferencePriceRecord


def test_normalise_item_name_basic():
    assert normalise_item_name("Paracetamol Tablet") == "paracetamol"
    assert normalise_item_name("Amoxicillin 500mg Capsule") == "amoxicillin"
    assert normalise_item_name("Ibuprofen 400 mg tab") == "ibuprofen"
    assert normalise_item_name("Ceftriaxone 1g inj") == "ceftriaxone"
    assert normalise_item_name("Cough Syrup 100ml") == "cough"


@pytest.fixture
def sample_reference_items():
    return {
        "paracetamol": ReferencePriceRecord(
            item_key="paracetamol",
            display_name="Paracetamol",
            category="Medicine",
            unit="Tablet",
            ceiling_or_reference_price=1.5,
            source="Test",
            source_url="",
            effective_date="2024",
        ),
        "amoxicillin": ReferencePriceRecord(
            item_key="amoxicillin",
            display_name="Amoxicillin 500mg",
            category="Medicine",
            unit="Capsule",
            ceiling_or_reference_price=10.0,
            source="Test",
            source_url="",
            effective_date="2024",
        ),
        "ibuprofen": ReferencePriceRecord(
            item_key="ibuprofen",
            display_name="Ibuprofen Tab",
            category="Medicine",
            unit="Tablet",
            ceiling_or_reference_price=5.0,
            source="Test",
            source_url="",
            effective_date="2024",
        ),
        "bandage": ReferencePriceRecord(
            item_key="bandage",
            display_name="Cotton Bandage",
            category="Supply",
            unit="Roll",
            ceiling_or_reference_price=20.0,
            source="Test",
            source_url="",
            effective_date="2024",
        ),
        "fever_med": ReferencePriceRecord(
            item_key="fever_med",
            display_name="Fever Medicine",
            category="Medicine",
            unit="Bottle",
            ceiling_or_reference_price=50.0,
            source="Test",
            source_url="",
            effective_date="2024",
        ),
        "syrup_cough": ReferencePriceRecord(
            item_key="syrup_cough",
            display_name="Cough Syrup",
            category="Medicine",
            unit="Bottle",
            ceiling_or_reference_price=30.0,
            source="Test",
            source_url="",
            effective_date="2024",
        ),
    }


@pytest.mark.parametrize(
    "input_name, expected_key, expected_score_threshold",
    [
        # Exact/near exact matches (with stripping)
        ("Paracetamol", "paracetamol", 100.0),
        ("Paracetamol Tablet", "paracetamol", 100.0),
        ("Amoxicillin 500mg", "amoxicillin", 100.0),
        ("Amoxicillin 500 mg cap", "amoxicillin", 100.0),
        ("Ibuprofen", "ibuprofen", 100.0),
        # Misspelled
        ("Paracetmol tab", "paracetamol", 90.0),
        ("Amoxicilin", "amoxicillin", 90.0),
        ("Ibprofen 400mg", "ibuprofen", 90.0),
        ("Bandje cotton", "bandage", 80.0),
        ("Cotten Bandage", "bandage", 90.0),
        # Abbreviations
        ("Cough syr", "syrup_cough", 100.0),
        ("Paracetamol tab", "paracetamol", 100.0),
        # Hindi-transliterated/Alternative (These will rely on partial matches)
        # To get good matches with transliteration via rapidfuzz,
        # there needs to be string similarity.
        # Note: True Hindi transliteration matching would require a
        # dictionary/translation step,
        # but we use fuzzing as instructed.
        ("Fevr Medcine", "fever_med", 80.0),
        (
            "Patti cotton",
            "bandage",
            50.0,
        ),  # Will likely fail threshold, just checking behavior below
        ("bukhar dawa", "fever_med", 20.0),  # Will fail threshold
        # Different strengths stripped away
        ("Paracetamol 650mg", "paracetamol", 100.0),
        ("Paracetamol 250 mg syrup", "paracetamol", 100.0),
        ("Amoxicillin 250mg cap", "amoxicillin", 100.0),
        ("Amoxicillin 1g inj", "amoxicillin", 100.0),
        # Variations in spacing/casing
        ("  paRacetaMol  ", "paracetamol", 100.0),
        ("AMOXICILLIN", "amoxicillin", 100.0),
        ("iBUproFen TABlet", "ibuprofen", 100.0),
        # More misspellings
        ("Paracitamol", "paracetamol", 90.0),
        ("Amoxycillin", "amoxicillin", 90.0),
        ("Ibuprofin", "ibuprofen", 85.0),
        ("Cough sirup", "syrup_cough", 60.0),
        ("Cof syrup", "syrup_cough", 60.0),  # Lower score
        # Edge cases
        ("500mg", None, 0.0),  # Strips to empty string
        ("Tablet", None, 0.0),  # Strips to empty string
        ("", None, 0.0),
    ],
)
def test_match_item(
    input_name, expected_key, expected_score_threshold, sample_reference_items
):
    # Set threshold low enough to observe the scores for test assertions if needed,
    # or just use default 80.0.
    threshold = 80.0

    result = match_item(input_name, sample_reference_items, threshold=threshold)

    if expected_key is None or expected_score_threshold < threshold:
        # If expected score is below our test threshold (80), it should return None
        assert result.best_match is None
        assert result.score < threshold or result.score == 0.0
    else:
        assert result.best_match is not None
        assert result.best_match.item_key == expected_key
        assert result.score >= threshold


def test_match_item_no_references():
    result = match_item("Paracetamol", {})
    assert result.best_match is None
    assert result.score == 0.0
    assert result.reason == "No reference items provided"


def test_match_item_empty_normalized():
    # Only strengths/pack words
    result = match_item(
        "500mg tablet",
        {
            "test": ReferencePriceRecord(
                item_key="test",
                display_name="test",
                category="",
                unit="",
                ceiling_or_reference_price=1.0,
                source="",
                source_url="",
                effective_date="",
            )
        },
    )
    assert result.best_match is None
    assert result.score == 0.0
    assert result.reason == "Normalized name is empty"
