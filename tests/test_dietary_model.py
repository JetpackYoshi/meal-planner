import pytest
from mealplanner.dietary_model import (
    FoodCategory, Ingredient, Meal, DietaryRestriction,
    Person, tag_registry, categorize_from_string
)
from mealplanner.meal_compatibility_analyzer import MealCompatibilityAnalyzer
from mealplanner.defaults import setup_defaults

@pytest.fixture(autouse=True)
def setup_food_categories_and_tags():
    setup_defaults()
    yield
    FoodCategory.reset()
    tag_registry._tag_map.clear()

def test_food_category_inheritance(setup_food_categories_and_tags):
    meat = FoodCategory.get("MEAT")
    chicken = FoodCategory.get("CHICKEN")
    assert chicken.is_a("MEAT")
    assert chicken.is_a("ANIMAL_PRODUCTS")
    assert not chicken.is_a("DAIRY")

def test_dietary_restriction_forbids():
    dairy = FoodCategory("DAIRY")
    restriction = DietaryRestriction({"DAIRY"})
    assert restriction.forbids(dairy)

def test_meal_compatibility_with_individual(setup_food_categories_and_tags):
    cheese = Ingredient("Cheddar", FoodCategory.get("CHEESE"), 120)
    almonds = Ingredient("Almonds", FoodCategory.get("ALMOND"), 150)
    meal = Meal("Cheese and Nuts", [cheese, almonds])
    vegan = DietaryRestriction({"ANIMAL_PRODUCTS"})
    nut_free = DietaryRestriction({"NUTS"})
    assert not meal.is_compatible_with(vegan)
    assert not meal.is_compatible_with(nut_free)

def test_meal_compatibility_with_group(setup_food_categories_and_tags):
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

    # Register the tags first
    tag_registry.register_tag("VEGAN", vegan_r, category="ethical", overwrite=True)
    tag_registry.register_tag("VEGETARIAN", vegetarian_r, category="ethical", overwrite=True)
    tag_registry.register_tag("NUT-FREE", DietaryRestriction({"NUTS"}), category="allergen", overwrite=True)
    tag_registry.register_tag("DAIRY-FREE", DietaryRestriction({"DAIRY"}), category="allergen", overwrite=True)
    tag_registry.register_tag("EGG-FREE", DietaryRestriction({"EGGS"}), category="allergen", overwrite=True)
    tag_registry.register_tag("FISH-FREE", DietaryRestriction({"FISH"}), category="allergen", overwrite=True)
    tag_registry.register_tag("SHELLFISH-FREE", DietaryRestriction({"SHELLFISH"}), category="allergen", overwrite=True)
    tag_registry.register_tag("MEAT-FREE", DietaryRestriction({"MEAT"}), category="ethical", overwrite=True)
    tag_registry.register_tag("PESCATARIAN", DietaryRestriction({"MEAT"}), category="ethical", overwrite=True)

    vegan_tags = set(tag_registry.generate_tags(vegan_r))
    expected_vegan_tags = {"VEGAN", "VEGETARIAN", "PESCATARIAN", "MEAT-FREE", "DAIRY-FREE", "EGG-FREE", "FISH-FREE", "SHELLFISH-FREE", "BEEF-FREE"}
    assert vegan_tags == expected_vegan_tags

    vegetarian_tags = set(tag_registry.generate_tags(vegetarian_r))
    expected_vegetarian_tags = {"VEGETARIAN", "PESCATARIAN", "MEAT-FREE", "FISH-FREE", "SHELLFISH-FREE", "BEEF-FREE"}
    assert vegetarian_tags == expected_vegetarian_tags

    custom_tags = set(tag_registry.generate_tags(custom_r))
    expected_custom_tags = {"VEGETARIAN", "PESCATARIAN", "MEAT-FREE", "NUT-FREE", "BEEF-FREE", "FISH-FREE", "SHELLFISH-FREE"}
    assert custom_tags == expected_custom_tags

def test_person_label():
    person = Person("Jamie", tag="VEGAN")
    assert person.label() == str(person.restriction)
    
    person = Person("Alex", restriction=DietaryRestriction({"MEAT"}))
    assert person.label() == str(person.restriction)
    
    person = Person("Sam")  # No restrictions
    assert person.label() == "No restrictions"

def test_categorize_from_string(setup_food_categories_and_tags):
    result = categorize_from_string("wild salmon filet")
    assert result.name == "SALMON"

def test_meal_compatibility_analyzer(setup_food_categories_and_tags):
    cheese = Ingredient("Cheddar", FoodCategory.get("CHEESE"), 120)
    salmon = Ingredient("Salmon", FoodCategory.get("SALMON"), 180)
    almonds = Ingredient("Almonds", FoodCategory.get("ALMOND"), 150)

    meal1 = Meal("Cheese Plate", [cheese, almonds])  # NUTS + DAIRY
    meal2 = Meal("Salmon Dish", [salmon])            # FISH

    alex = Person("Alex", tag="VEGAN")
    jamie = Person("Jamie", tag="PESCATARIAN")
    sam = Person("Sam", tag="NUT-FREE")

    analyzer = MealCompatibilityAnalyzer([meal1, meal2], [alex, jamie, sam])
    matrix = analyzer.get_compatibility_matrix()
    assert matrix.loc[matrix["Meal"] == "Cheese Plate", "Alex"].iloc[0] == False
    assert matrix.loc[matrix["Meal"] == "Salmon Dish", "Jamie"].iloc[0] == True
    assert "Sam" in matrix.columns

    top = analyzer.get_most_compatible_meals(top_n=1)
    assert top.iloc[0]["Meal"] == "Salmon Dish"

    universal = analyzer.get_universally_compatible_meals()
    assert "Salmon Dish" not in universal["Meal"].values
