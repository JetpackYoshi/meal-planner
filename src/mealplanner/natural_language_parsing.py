import logging
from rapidfuzz import process, fuzz
import re

from mealplanner.dietary_model import *

logger = logging.getLogger("diet_parser")
logger.setLevel(logging.DEBUG)

# -----------------------------------
# Utility: parse_freeform_restriction
# -----------------------------------

# Keywords and their corresponding exclusion sets
KEYWORD_MAP = {
    "vegetarian": {"MEAT", "FISH", "SHELLFISH"},
    "vegan": {"ANIMAL_PRODUCTS"},
    "pescatarian": {"MEAT"},
    "dairy": {"DAIRY"},
    "lactose": {"DAIRY"},
    "milk": {"DAIRY"},
    "cheese": {"DAIRY"},
    "egg": {"EGGS"},
    "eggs": {"EGGS"},
    "beef": {"MEAT"},
    "meat": {"MEAT"},
    "fish": {"FISH"},
    "shellfish": {"SHELLFISH"},
    "nut": {"NUTS"},
    "nuts": {"NUTS"},
    "peanut": {"NUTS"},
    "peanuts": {"NUTS"},
    "tree nut": {"NUTS"},
    "gluten": {"GLUTEN"},
}

NO_RESTRICTION_PHRASES = {
    "", "no", "none", "nope", "naw", "nah", "n/a", "none!", "nope!",
    "i can eat anything", "i can eat everything", "everything is fine", "i eat everything"
}

def parse_freeform_restriction(
    text: str,
    *,
    fuzz_threshold: int = 75,
    return_debug: bool = False
    ):
    """
    Parses a freeform dietary restriction string with optional fuzzy matching and debug metadata.

    Parameters
    ----------
    text : str
        User-entered freeform dietary restriction.
    fuzz_threshold : int
        Minimum similarity ratio (0-100) for fuzzy keyword matching.
    return_debug : bool
        If True, return a tuple with debug metadata.

    Returns
    -------
    DietaryRestriction or None
        If return_debug is False.
    (DietaryRestriction or None, dict)
        If return_debug is True.
    """
    original = text
    text = text.strip().lower()

    # Debug metadata for tracing parsing steps
    debug = {
        "input": original,
        "normalized": text,
        "matched_terms": [],
        "exclusions": set(),
        "fuzzy_matches": [],
        "score": 0.0,
    }

    # Words to ignore during fuzzy matching
    IGNORE_FUZZY = {
        "eat", "food", "diet", "anything", "everything", "no", "not",
        "can", "don", "dont", "do", "all", "i", "you", "we"
    }

    # Handle known "no restriction" phrases
    if text in NO_RESTRICTION_PHRASES:
        debug["reason"] = "Matched known unrestricted phrase"
        debug["exclusions"] = []
        result = None
        return (result, debug) if return_debug else result

    exclusions = set()
    # Tokenize input text
    tokens = re.findall(r"\b\w+\b", text)

    # Direct keyword matching
    for word, ex_set in KEYWORD_MAP.items():
        if word in tokens:
            exclusions |= ex_set
            debug["matched_terms"].append(word)

    # Fuzzy matching for tokens not directly matched
    unmatched_tokens = [t for t in tokens if t not in debug["matched_terms"]]
    for token in unmatched_tokens:
        if token in IGNORE_FUZZY:
            continue
        matches = process.extract(
            token,
            KEYWORD_MAP.keys(),
            scorer=fuzz.ratio,
            processor=None,
            score_cutoff=fuzz_threshold,
            limit=3,
        )
        if matches:
            # Pick the best match by score and then by length
            match, score, _ = max(matches, key=lambda x: (x[1], len(x[0])))
            exclusions |= KEYWORD_MAP[match]
            debug["fuzzy_matches"].append((token, match, score))

    # Finalize debug info
    debug["exclusions"] = sorted(list(exclusions)) if exclusions else []
    debug["score"] = (
        (len(debug["matched_terms"]) + len(debug["fuzzy_matches"])) / len(KEYWORD_MAP)
        if KEYWORD_MAP else 0.0
    )
    debug["reason"] = (
        "Matched exclusions via keyword and/or fuzzy matching" if exclusions
        else "No exclusions matched"
    )

    # Build result object
    result = DietaryRestriction(exclusions) if exclusions else None

    # Logging
    if result:
        logger.debug(
            f"[{original}] → {debug['exclusions']} "
            f"(terms: {debug['matched_terms']}, fuzz: {debug['fuzzy_matches']})"
        )
    else:
        logger.debug(f"[{original}] → No restriction")

    return (result, debug) if return_debug else result