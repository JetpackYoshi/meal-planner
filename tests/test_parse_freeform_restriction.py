import pytest
from mealplanner.natural_language_parsing import *
import pandas as pd

@pytest.mark.parametrize("input_text,expected_exclusions", [
    ("No", None),
    ("None", None),
    ("Nope!", None),
    ("", None),
    ("Vegetarian", {"MEAT", "FISH", "SHELLFISH"}),
    ("vegan", {"ANIMAL_PRODUCTS"}),
    ("nut allergy", {"NUTS"}),
    ("I don't eat peenuts", {"NUTS"}),
    ("I am lactose intolerant", {"DAIRY"}),
    ("I don't eat meat or fish", {"MEAT", "FISH"}),
    ("gluten free", {"GLUTEN"}),
    ("no beef or egg", {"MEAT", "EGGS"}),
    ("shellfish & nuts", {"SHELLFISH", "NUTS"}),
])
def test_parse_keywords(input_text, expected_exclusions):
    restriction, debug = parse_freeform_restriction(input_text, return_debug=True)
    if expected_exclusions is None:
        assert restriction is None
    else:
        assert restriction is not None
        assert restriction.excluded == expected_exclusions

@pytest.mark.parametrize("input_text,fuzzy_term,expected_category", [
    ("vegitarian", "vegetarian", {"MEAT", "FISH", "SHELLFISH"}),
    ("lactos", "lactose", {"DAIRY"}),
    ("glutten", "gluten", {"GLUTEN"}),
    ("sheelfish", "shellfish", {"SHELLFISH"}),
])
def test_fuzzy_matching(input_text, fuzzy_term, expected_category):
    # Use lower threshold to allow more typo tolerance
    restriction, debug = parse_freeform_restriction(input_text, return_debug=True, fuzz_threshold=80)
    restriction, debug = parse_freeform_restriction(input_text, return_debug=True)
    assert restriction is not None
    assert expected_category.issubset(restriction.excluded)
    assert any(fuzzy_term in m for (_, m, _) in debug["fuzzy_matches"])

@pytest.mark.parametrize("input_text", [
    "xyzzy", "food ok", "random text", "I can eat everything", "unicorns only", "flexitarian"
])
def test_non_matching_edge_cases(input_text):
    # Expanded unrestricted phrases should now capture these
    restriction, debug = parse_freeform_restriction(input_text, return_debug=True, fuzz_threshold=80)
    restriction, debug = parse_freeform_restriction(input_text, return_debug=True)
    assert restriction is None
    assert debug["exclusions"] == []


def test_integration_from_sample_table():
    data = {
        "Name": [
            "Abbi Olivieri", "Alexis Abraham", "Charlotte delavaloire", "Delia Parrish",
            "Justine Frank", "Marisa Edmondson", "Omny Miranda Martone", "Raktima"
        ],
        "Restrictions": [
            "Vegetarian and Dairy free", "No", "Vegetarian", "Lactose intolerant",
            "vegan", "Nuts (except almonds) shellfish", "Vegan (no meat, milk, egg)", "No beef"
        ]
    }
    df = pd.DataFrame(data)

    # Evaluate restrictions
    results = [parse_freeform_restriction(r, return_debug=True) for r in df["Restrictions"]]

    assert results[0][0] is not None
    assert {"DAIRY", "MEAT", "FISH", "SHELLFISH"}.issubset(results[0][0].excluded)

    assert results[1][0] is None  # "No"
    assert {"MEAT", "FISH", "SHELLFISH"}.issubset(results[2][0].excluded)  # Vegetarian
    assert {"DAIRY"}.issubset(results[3][0].excluded)  # Lactose intolerant
    assert {"ANIMAL_PRODUCTS"}.issubset(results[4][0].excluded)  # Vegan
    assert {"NUTS", "SHELLFISH"}.issubset(results[5][0].excluded)  # Nuts + shellfish
    assert {"ANIMAL_PRODUCTS"}.issubset(results[6][0].excluded)  # Vegan again
    assert {"MEAT"}.issubset(results[7][0].excluded)  # "No beef"

    # Ensure all return debug info
    for restriction, debug in results:
        assert "input" in debug
