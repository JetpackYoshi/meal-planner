import pytest
from mealplanner.dietary_model import *

@pytest.fixture(autouse=True)
def reset_food_category():
    FoodCategory.reset()
    yield
    FoodCategory.reset()

@pytest.fixture
def setup_categories():
    FoodCategory.define("ANIMAL_PRODUCTS")
    FoodCategory.define("MEAT", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("DAIRY", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("FISH", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("SHELLFISH", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("NUTS")
    FoodCategory.define("CHEESE", {"DAIRY"})
    FoodCategory.define("SALMON", {"FISH"})
    FoodCategory.define("CHICKEN", {"MEAT"})
    FoodCategory.define("ALMOND", {"NUTS"})
    yield

@pytest.fixture(autouse=True)
def reset_tag_registry():
    tag_registry._tag_map.clear()
    tag_registry.register_tag("VEGAN", DietaryRestriction({"ANIMAL_PRODUCTS"}), category="ethical")
    tag_registry.register_tag("VEGETARIAN", DietaryRestriction({"MEAT", "FISH", "SHELLFISH"}), category="ethical")
    tag_registry.register_tag("PESCATARIAN", DietaryRestriction({"MEAT"}), category="ethical")
    tag_registry.register_tag("NUT-FREE", DietaryRestriction({"NUTS"}), category="allergen")
    tag_registry.register_tag("DAIRY-FREE", DietaryRestriction({"DAIRY"}), category="allergen")
    yield

def test_food_category_inheritance(setup_categories):
    meat = FoodCategory.get("MEAT")
    chicken = FoodCategory.get("CHICKEN")
    assert chicken.is_a("MEAT")
    assert chicken.is_a("ANIMAL_PRODUCTS")
    assert not chicken.is_a("DAIRY")

def test_dietary_restriction_forbids():
    dairy = FoodCategory("DAIRY")
    restriction = DietaryRestriction({"DAIRY"})
    assert restriction.forbids(dairy)

def test_meal_compatibility_with_individual(setup_categories):
    cheese = Ingredient("Cheddar", FoodCategory.get("CHEESE"), 120)
    almonds = Ingredient("Almonds", FoodCategory.get("ALMOND"), 150)
    meal = Meal("Cheese and Nuts", [cheese, almonds])
    vegan = DietaryRestriction({"ANIMAL_PRODUCTS"})
    nut_free = DietaryRestriction({"NUTS"})
    assert not meal.is_compatible_with(vegan)
    assert not meal.is_compatible_with(nut_free)

def test_meal_compatibility_with_group(setup_categories):
    rice = Ingredient("Plain Rice", FoodCategory("GRAIN"), 200)
    meal = Meal("Rice", [rice])
    group = [
        DietaryRestriction({"NUTS"}),
        DietaryRestriction({"DAIRY"}),
        DietaryRestriction({"MEAT"}),
    ]
    assert meal.is_compatible_with_group(group)

def test_tag_generation_exact_and_partial():
    vegan_r = DietaryRestriction({"ANIMAL_PRODUCTS"})
    vegetarian_r = DietaryRestriction({"MEAT", "FISH", "SHELLFISH"})
    custom_r = DietaryRestriction({"MEAT", "FISH", "SHELLFISH", "NUTS"})

    assert tag_registry.generate_tags(vegan_r) == ["VEGAN"]
    assert tag_registry.generate_tags(vegetarian_r) == ["VEGETARIAN"]
    assert tag_registry.generate_tags(custom_r) == ["VEGETARIAN", "NUT-FREE"]

def test_person_label():
    person = Person("Jamie", tag="VEGAN")
    assert person.label() == "Jamie [VEGAN]"

def test_categorize_from_string(setup_categories):
    result = categorize_from_string("wild salmon filet")
    assert result.name == "SALMON"

def test_meal_compatibility_analyzer(setup_categories):
    cheese = Ingredient("Cheddar", FoodCategory.get("CHEESE"), 120)
    salmon = Ingredient("Salmon", FoodCategory.get("SALMON"), 180)
    almonds = Ingredient("Almonds", FoodCategory.get("ALMOND"), 150)

    meal1 = Meal("Cheese Plate", [cheese, almonds])  # NUTS + DAIRY
    meal2 = Meal("Salmon Dish", [salmon])            # FISH

    alex = Person("Alex", tag="VEGAN")
    jamie = Person("Jamie", tag="PESCATARIAN")
    sam = Person("Sam", tag="NUT-FREE")

    analyzer = MealCompatibilityAnalyzer([meal1, meal2], [alex, jamie, sam])
    matrix = analyzer.build_matrix()
    assert matrix.loc["Cheese Plate", "Alex [VEGAN]"] == False
    assert matrix.loc["Salmon Dish", "Jamie [PESCATARIAN]"] == True
    assert "Sam [NUT-FREE]" in matrix.columns

    top = analyzer.get_most_compatible_meals(top_n=1)
    assert top.index[0] == "Salmon Dish"

    universal = analyzer.get_universally_compatible_meals()
    assert "Salmon Dish" not in universal.index
