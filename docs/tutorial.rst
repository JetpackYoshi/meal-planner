Tutorial
========

This tutorial will guide you through using the Meal Planner framework to model dietary restrictions, create meals, and analyze meal compatibility for groups of people with different dietary needs.

Installation
------------

First, install the package::

    git clone https://github.com/JetpackYoshi/meal-planner.git
    cd meal-planner
    pip install -e .

Basic Concepts
--------------

The Meal Planner framework is built around several key concepts:

1. **Food Categories**: Hierarchical categories that represent types of food (e.g., DAIRY → ANIMAL_PRODUCTS)
2. **Dietary Restrictions**: Rules about which food categories are excluded
3. **Ingredients**: Individual food items with metadata
4. **Meals**: Collections of ingredients
5. **People**: Individuals with dietary restrictions
6. **Tags**: Pre-defined common dietary restrictions

Step-by-Step Guide
------------------

1. Setting Up Food Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, let's set up a basic food category hierarchy::

    from mealplanner.dietary_model import FoodCategory

    # Clear existing categories (optional)
    FoodCategory.reset()

    # Define base categories
    FoodCategory.define("ANIMAL_PRODUCTS")
    FoodCategory.define("PLANT_BASED")

    # Define subcategories with inheritance
    FoodCategory.define("MEAT", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("DAIRY", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("EGGS", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("FISH", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("SHELLFISH", {"FISH"})
    
    FoodCategory.define("NUTS", {"PLANT_BASED"})
    FoodCategory.define("GRAINS", {"PLANT_BASED"})
    FoodCategory.define("GLUTEN", {"GRAINS"})

You can check category relationships::

    dairy = FoodCategory.get("DAIRY")
    print(dairy.is_a("ANIMAL_PRODUCTS"))  # True
    print(dairy.ancestors())  # {'ANIMAL_PRODUCTS'}

2. Creating Dietary Tags
~~~~~~~~~~~~~~~~~~~~~~~~

Register common dietary restrictions as tags::

    from mealplanner.dietary_model import DietaryRestriction, TagRegistry

    # Get the global tag registry
    tag_registry = TagRegistry()

    # Register common dietary tags
    tag_registry.register_tag(
        "VEGAN",
        DietaryRestriction({"ANIMAL_PRODUCTS"}),
        category="ethical"
    )
    
    tag_registry.register_tag(
        "VEGETARIAN",
        DietaryRestriction({"MEAT", "FISH"}),
        category="ethical"
    )
    
    tag_registry.register_tag(
        "GLUTEN-FREE",
        DietaryRestriction({"GLUTEN"}),
        category="medical"
    )

3. Creating Ingredients
~~~~~~~~~~~~~~~~~~~~~~~  

Create ingredients with their categories and metadata::

    from mealplanner.dietary_model import Ingredient

    # Create some basic ingredients
    chicken = Ingredient(
        name="Chicken Breast",
        category=FoodCategory.get("MEAT"),
        calories=165.0
    )

    rice = Ingredient(
        name="Brown Rice",
        category=FoodCategory.get("GRAINS"),
        calories=111.0
    )

    almonds = Ingredient(
        name="Almonds",
        category=FoodCategory.get("NUTS"),
        calories=164.0,
        allergens={"nuts"}
    )

4. Creating Meals
~~~~~~~~~~~~~~~~~

Combine ingredients into meals::

    from mealplanner.dietary_model import Meal

    # Create a simple meal
    chicken_rice_bowl = Meal(
        name="Chicken & Rice Bowl",
        ingredients=[chicken, rice]
    )

    # Create another meal
    almond_rice_bowl = Meal(
        name="Almond & Rice Bowl",
        ingredients=[almonds, rice]
    )

5. Defining People with Dietary Needs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create profiles for people with different dietary restrictions::

    from mealplanner.dietary_model import Person
    from mealplanner.natural_language_parsing import parse_nl_restriction

    # Person using a predefined tag
    vegan_person = Person("Alex", tag="VEGAN")

    # Person with custom restriction using natural language
    custom_restriction = parse_nl_restriction("no nuts or gluten")
    allergic_person = Person("Sam", restriction=custom_restriction)

6. Analyzing Meal Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Analyze which meals are suitable for which people::

    from mealplanner.dietary_model import MealCompatibilityAnalyzer

    # Create analyzer
    meals = [chicken_rice_bowl, almond_rice_bowl]
    people = [vegan_person, allergic_person]
    analyzer = MealCompatibilityAnalyzer(meals, people)

    # Print compatibility matrix
    print("\nMeal Compatibility Matrix:")
    analyzer.print_matrix(mode="markdown")

    # Get most compatible meals
    print("\nMost Compatible Meals:")
    print(analyzer.get_most_compatible_meals())

    # Find universally compatible meals
    print("\nUniversally Compatible Meals:")
    print(analyzer.get_universally_compatible_meals())

7. Using Natural Language Parsing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parse freeform dietary restrictions::

    from mealplanner.natural_language_parsing import parse_nl_restriction

    # Parse simple restrictions
    restriction1 = parse_nl_restriction("vegetarian")
    restriction2 = parse_nl_restriction("no dairy or eggs")

    # Parse with debug information
    restriction3, debug_info = parse_nl_restriction(
        "gluten free and no nuts",
        return_debug=True
    )
    print(f"Debug info: {debug_info}")

Advanced Usage
--------------

1. Custom Food Categories
~~~~~~~~~~~~~~~~~~~~~~~~~

You can create custom food category hierarchies for specific needs::

    # Create cuisine-based categories
    FoodCategory.define("CUISINE")
    FoodCategory.define("ASIAN", {"CUISINE"})
    FoodCategory.define("JAPANESE", {"ASIAN"})
    FoodCategory.define("CHINESE", {"ASIAN"})

2. Complex Dietary Restrictions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Combine multiple restrictions::

    # Create a complex restriction
    complex_restriction = DietaryRestriction(
        excluded={"MEAT", "DAIRY", "NUTS"}
    )

3. Meal Analysis and Export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export compatibility analysis::

    # Export to CSV
    analyzer.export_csv("meal_compatibility.csv")

    # Export to Markdown
    analyzer.export_markdown("meal_compatibility.md")

Best Practices
--------------

1. **Food Categories**:
   - Create a clear hierarchy
   - Use uppercase for category names
   - Keep categories granular but meaningful

2. **Ingredients**:
   - Always include allergen information
   - Use accurate calorie data
   - Assign the most specific category possible

3. **Meals**:
   - Give descriptive names
   - Include all ingredients, even small amounts
   - Consider portion sizes

4. **Dietary Restrictions**:
   - Use predefined tags when possible
   - Test restrictions with sample meals
   - Document custom restrictions

5. **Analysis**:
   - Regularly update compatibility matrices
   - Export results for record-keeping
   - Review universally compatible meals

Troubleshooting
---------------

Common Issues and Solutions:

1. **Category Not Found**:
   - Ensure category is defined before use
   - Check for case sensitivity (use uppercase)
   - Verify parent categories exist

2. **Unexpected Meal Compatibility**:
   - Check ingredient categories
   - Verify restriction definitions
   - Review category hierarchy

3. **Natural Language Parsing Issues**:
   - Use simpler, clearer descriptions
   - Check for typos
   - Use debug mode to see matching

4. **Performance Optimization**:
   - Minimize category hierarchy depth
   - Use predefined tags when possible
   - Cache compatibility results for large datasets 