Natural Language Parsing
=====================

The Meal Planner framework includes a powerful natural language parsing system that converts freeform dietary descriptions into structured dietary restrictions. This page explains how the parsing system works and how to use it effectively.

Basic Usage
----------

The simplest way to use the natural language parser is::

    from mealplanner.natural_language_parsing import parse_nl_restriction

    # Parse a simple restriction
    restriction = parse_nl_restriction("vegetarian and no dairy")

    # Parse with debug information
    restriction, debug_info = parse_nl_restriction(
        "no nuts or gluten",
        return_debug=True
    )

How It Works
-----------

The natural language parser uses a combination of direct keyword matching and fuzzy matching to understand dietary restrictions. Here's how it processes input:

1. Text Preprocessing
~~~~~~~~~~~~~~~~~~~

The parser first normalizes the input text by:

* Converting to lowercase
* Stripping whitespace
* Tokenizing into individual words

For example::

    "I'm Vegetarian and Dairy-Free!" → ["i'm", "vegetarian", "and", "dairy", "free"]

2. Direct Keyword Matching
~~~~~~~~~~~~~~~~~~~~~~~~

The parser maintains a dictionary of known dietary keywords and their corresponding food category exclusions::

    KEYWORD_MAP = {
        "vegetarian": {"MEAT", "FISH", "SHELLFISH"},
        "vegan": {"ANIMAL_PRODUCTS"},
        "pescatarian": {"MEAT"},
        "dairy": {"DAIRY"},
        "lactose": {"DAIRY"},
        # ... and more
    }

Each token is checked against this map for exact matches.

3. Fuzzy Matching
~~~~~~~~~~~~~~~

For tokens that don't have exact matches, the parser uses fuzzy string matching (powered by the ``rapidfuzz`` library) to handle:

* Misspellings
* Variations in word forms
* Common abbreviations

The fuzzy matching has a configurable threshold (default: 75%) to control match sensitivity.

4. Exclusion Set Building
~~~~~~~~~~~~~~~~~~~~~~~

The parser combines all matched exclusions into a single set. For example::

    "vegetarian and dairy free"
    → {"MEAT", "FISH", "SHELLFISH"} (from "vegetarian")
    + {"DAIRY"} (from "dairy")
    = {"MEAT", "FISH", "SHELLFISH", "DAIRY"}

5. Special Cases
~~~~~~~~~~~~~~

The parser handles several special cases:

* Empty or "no restriction" phrases::

    "", "none", "no", "i can eat anything"
    → Returns None (no restrictions)

* Common word filtering::

    Ignores words like "eat", "food", "diet", "can", "don't"
    when doing fuzzy matching

Debug Information
---------------

When ``return_debug=True``, the parser returns detailed information about the parsing process::

    restriction, debug = parse_nl_restriction(
        "vegetarian no dairy",
        return_debug=True
    )

    print(debug)
    {
        "input": "vegetarian no dairy",
        "normalized": "vegetarian no dairy",
        "matched_terms": ["vegetarian", "dairy"],
        "exclusions": ["MEAT", "FISH", "SHELLFISH", "DAIRY"],
        "fuzzy_matches": [],
        "score": 0.5,
        "reason": "Matched exclusions via keyword matching"
    }

The debug information includes:

* ``input``: Original input string
* ``normalized``: Preprocessed input
* ``matched_terms``: Keywords directly matched
* ``exclusions``: Final set of excluded categories
* ``fuzzy_matches``: Any terms matched via fuzzy matching
* ``score``: Confidence score (0-1)
* ``reason``: Explanation of the parsing result

Best Practices
------------

1. Keep Descriptions Simple
~~~~~~~~~~~~~~~~~~~~~~~~~

Use clear, simple phrases::

    Good: "vegetarian and gluten free"
    Less good: "I try to avoid eating any meat or things with gluten in them usually"

2. Use Common Terms
~~~~~~~~~~~~~~~~~

The parser works best with common dietary terms::

    Good: "vegan", "dairy-free", "no nuts"
    Less good: "lacto-ovo-pesco vegetarian"

3. Combine with Tags
~~~~~~~~~~~~~~~~~~

For complex restrictions, consider using predefined tags::

    from mealplanner.dietary_model import Person, tag_registry

    # Register a complex tag
    tag_registry.register_tag(
        "KETO",
        DietaryRestriction({"GRAINS", "SUGAR"}),
        category="diet"
    )

    # Use the tag instead of parsing
    person = Person("Alex", tag="KETO")

4. Verify Results
~~~~~~~~~~~~~~~

Always verify parsed restrictions in critical applications::

    restriction, debug = parse_nl_restriction(
        user_input,
        return_debug=True
    )

    if debug["score"] < 0.3:
        print("Warning: Low confidence in parsing result")

Troubleshooting
-------------

Common Issues and Solutions:

1. **Unexpected Exclusions**

   * Check the debug output to see which terms were matched
   * Use more specific terminology
   * Consider using predefined tags for complex cases

2. **No Restrictions Detected**

   * Ensure terms are in the keyword dictionary
   * Check for typos or unusual spellings
   * Use simpler, more common terms

3. **Too Many Restrictions**

   * Break down complex descriptions into simpler terms
   * Use more specific terminology
   * Consider creating a custom tag instead

4. **Low Confidence Scores**

   * Use more standard dietary terms
   * Check for misspellings
   * Simplify the description

Example Usage Patterns
--------------------

1. Basic Parsing
~~~~~~~~~~~~~~

::

    restriction = parse_nl_restriction("vegetarian")
    print(restriction.excluded)  # {'MEAT', 'FISH', 'SHELLFISH'}

2. Multiple Restrictions
~~~~~~~~~~~~~~~~~~~~~

::

    restriction = parse_nl_restriction("vegan and gluten free")
    print(restriction.excluded)  # {'ANIMAL_PRODUCTS', 'GLUTEN'}

3. With Debug Information
~~~~~~~~~~~~~~~~~~~~~~

::

    restriction, debug = parse_nl_restriction(
        "no dairy or nuts",
        return_debug=True,
        fuzz_threshold=80
    )

4. In Person Creation
~~~~~~~~~~~~~~~~~~~

::

    from mealplanner.dietary_model import Person

    restriction = parse_nl_restriction("vegetarian no dairy")
    person = Person("Alex", restriction=restriction)

5. With Meal Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~

::

    from mealplanner.dietary_model import MealCompatibilityAnalyzer

    restriction = parse_nl_restriction("no nuts or shellfish")
    person = Person("Sam", restriction=restriction)
    analyzer = MealCompatibilityAnalyzer(meals, [person])
    compatible_meals = analyzer.get_compatible_meals() 