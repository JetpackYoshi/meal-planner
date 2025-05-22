import pytest
import pandas as pd
from mealplanner.meal_compatibility_analyzer import MealCompatibilityAnalyzer, analyze_meal_compatibility
from mealplanner.dietary_model import (
    Person, DietaryRestriction, FoodCategory, Ingredient, Meal,
    tag_registry
)
from mealplanner.defaults import setup_defaults, setup_default_food_categories

@pytest.fixture(autouse=True)
def setup_food_categories_and_tags():
    setup_defaults()
    yield
    FoodCategory.reset()
    tag_registry._tag_map.clear()

@pytest.fixture
def sample_people():
    """Create a sample list of people with different dietary restrictions."""
    return [
        Person("Alice", DietaryRestriction({"ANIMAL_PRODUCTS"})),  # Vegan
        Person("Bob", DietaryRestriction({"MEAT"})),  # Vegetarian
        Person("Charlie", DietaryRestriction({"WHEAT"})),  # Gluten-free
        Person("Diana", DietaryRestriction({"DAIRY"})),  # Dairy-free
        Person("Eve")  # No restrictions
    ]

@pytest.fixture
def sample_meals():
    """Create a sample list of meals with various ingredients."""
    setup_default_food_categories()
    return [
        Meal("Vegan Pasta", [
            Ingredient("Pasta", FoodCategory.get("WHEAT"), calories=200),
            Ingredient("Tomato Sauce", FoodCategory.get("VEGETABLES"), calories=50),
            Ingredient("Mushrooms", FoodCategory.get("VEGETABLES"), calories=30)
        ]),
        Meal("Cheese Pizza", [
            Ingredient("Pizza Dough", FoodCategory.get("WHEAT"), calories=250),
            Ingredient("Tomato Sauce", FoodCategory.get("VEGETABLES"), calories=50),
            Ingredient("Mozzarella", FoodCategory.get("CHEESE"), calories=200)
        ]),
        Meal("Chicken Rice Bowl", [
            Ingredient("Chicken", FoodCategory.get("CHICKEN"), calories=250),
            Ingredient("Rice", FoodCategory.get("RICE"), calories=200),
            Ingredient("Broccoli", FoodCategory.get("VEGETABLES"), calories=50)
        ]),
        Meal("Nut-Free Salad", [
            Ingredient("Lettuce", FoodCategory.get("VEGETABLES"), calories=20),
            Ingredient("Tomatoes", FoodCategory.get("VEGETABLES"), calories=30),
            Ingredient("Cucumber", FoodCategory.get("VEGETABLES"), calories=20),
            Ingredient("Olive Oil", FoodCategory.get("PLANT_BASED"), calories=120)
        ])
    ]

def test_build_matrix(sample_meals, sample_people):
    """Test that the compatibility matrix is correctly built."""
    analyzer = MealCompatibilityAnalyzer(sample_meals, sample_people)
    matrix = analyzer.get_compatibility_matrix()
    
    # Check matrix dimensions
    assert len(matrix) == len(sample_meals)
    assert "Meal" in matrix.columns
    assert all(person.name in matrix.columns for person in sample_people)
    
    # Check specific compatibilities
    vegan_pasta_row = matrix[matrix["Meal"] == "Vegan Pasta"].iloc[0]
    assert vegan_pasta_row["Alice"]  # Vegan can eat vegan pasta
    assert vegan_pasta_row["Bob"]  # Vegetarian can eat vegan pasta
    assert not vegan_pasta_row["Charlie"]  # Gluten-free can't eat wheat
    assert vegan_pasta_row["Diana"]  # Dairy-free can eat vegan pasta
    assert vegan_pasta_row["Eve"]  # No restrictions can eat anything

def test_score_meals(sample_meals, sample_people):
    """Test that meals are correctly scored based on compatibility."""
    analyzer = MealCompatibilityAnalyzer(sample_meals, sample_people)
    scores = analyzer.score_meals()
    
    # Check that scores are between 0 and 1
    assert all(0 <= score <= 1 for score in scores)
    
    # Check specific scores
    assert scores["Vegan Pasta"] == 0.8  # 4 out of 5 people can eat it
    assert scores["Cheese Pizza"] == 0.4  # 2 out of 5 people can eat it
    assert scores["Chicken Rice Bowl"] == 0.6  # 3 out of 5 people can eat it
    assert scores["Nut-Free Salad"] == 1.0  # Everyone can eat it

def test_get_most_compatible_meals(sample_meals, sample_people):
    """Test that most compatible meals are correctly identified."""
    analyzer = MealCompatibilityAnalyzer(sample_meals, sample_people)
    most_compatible = analyzer.get_most_compatible_meals()
    
    # Check that meals are sorted by compatibility score
    scores = most_compatible["Compatibility Score"].values
    assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
    
    # Check specific meals
    assert most_compatible.iloc[0]["Meal"] == "Nut-Free Salad"  # Most compatible
    assert most_compatible.iloc[-1]["Meal"] == "Cheese Pizza"  # Least compatible

def test_get_universally_compatible_meals(sample_meals, sample_people):
    """Test that universally compatible meals are correctly identified."""
    analyzer = MealCompatibilityAnalyzer(sample_meals, sample_people)
    universal = analyzer.get_universally_compatible_meals()
    
    # Check that only fully compatible meals are included
    assert len(universal) == 1
    assert universal.iloc[0]["Meal"] == "Nut-Free Salad"
    assert universal.iloc[0]["Compatibility Score"] == 1.0

def test_export_markdown_with_emojis(sample_meals, sample_people, tmp_path):
    """Test that the matrix is correctly exported to markdown with emojis."""
    analyzer = MealCompatibilityAnalyzer(sample_meals, sample_people)
    output_file = tmp_path / "test_output.md"
    analyzer.export_markdown(str(output_file), use_emojis=True)
    
    # Read the exported file
    content = output_file.read_text()
    
    # Check that emojis are present
    assert "✅" in content
    assert "❌" in content
    
    # Check that meal names are present
    for meal in sample_meals:
        assert meal.name in content

def test_export_markdown_without_emojis(sample_meals, sample_people, tmp_path):
    """Test that the matrix is correctly exported to markdown without emojis."""
    analyzer = MealCompatibilityAnalyzer(sample_meals, sample_people)
    output_file = tmp_path / "test_output.md"
    analyzer.export_markdown(str(output_file), use_emojis=False)
    
    # Read the exported file
    content = output_file.read_text()
    
    # Check that True/False are present
    assert "True" in content
    assert "False" in content
    
    # Check that emojis are not present
    assert "✅" not in content
    assert "❌" not in content

def test_analyze_meal_compatibility_function(sample_meals, sample_people):
    """Test the analyze_meal_compatibility convenience function."""
    analyzer = analyze_meal_compatibility(sample_meals, sample_people)
    assert isinstance(analyzer, MealCompatibilityAnalyzer)
    assert len(analyzer.meals) == len(sample_meals)
    assert len(analyzer.people) == len(sample_people)

def test_get_compatibility_matrix_with_emojis(sample_meals, sample_people):
    """Test that the matrix is correctly built with emojis."""
    analyzer = MealCompatibilityAnalyzer(sample_meals, sample_people)
    matrix = analyzer.get_compatibility_matrix(use_emojis=True)
    
    # Check matrix dimensions
    assert len(matrix) == len(sample_meals)
    assert "Meal" in matrix.columns
    assert all(person.name in matrix.columns for person in sample_people)
    
    # Check that emojis are present
    assert "✅" in matrix.values
    assert "❌" in matrix.values
    
    # Check specific compatibilities
    vegan_pasta_row = matrix[matrix["Meal"] == "Vegan Pasta"].iloc[0]
    assert vegan_pasta_row["Alice"] == "✅"  # Vegan can eat vegan pasta
    assert vegan_pasta_row["Bob"] == "✅"  # Vegetarian can eat vegan pasta
    assert vegan_pasta_row["Charlie"] == "❌"  # Gluten-free can't eat wheat
    assert vegan_pasta_row["Diana"] == "✅"  # Dairy-free can eat vegan pasta
    assert vegan_pasta_row["Eve"] == "✅"  # No restrictions can eat anything 