#!/usr/bin/env python3
"""
Example demonstrating the integration between GuestListAnalyzer and MealCompatibilityAnalyzer.
This example shows how to:
1. Create a guest list with various dietary restrictions
2. Create a list of meals with different ingredients
3. Analyze compatibility between meals and guests
4. Generate various reports and visualizations
"""

import pandas as pd
from mealplanner.dietary_model import (
    FoodCategory, Ingredient, Meal, DietaryRestriction,
    tag_registry
)
from mealplanner.guest_list_analyzer import GuestListAnalyzer
from mealplanner.defaults import setup_defaults

def create_sample_meals():
    """Create a list of sample meals with various ingredients."""
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

def main():
    # Set up the default food categories and dietary tags
    setup_defaults()
    
    # Create a sample guest list
    guest_list = pd.DataFrame({
        'Name': [
            'Alice', 'Bob', 'Charlie', 'Diana', 'Eve'
        ],
        'Dietary Restriction': [
            'vegan',
            'vegetarian',
            'gluten-free',
            'dairy-free',
            'no restrictions'
        ]
    })
    
    # Create the guest list analyzer
    guest_analyzer = GuestListAnalyzer(guest_list)
    
    # Print guest list analysis
    print("\n=== Guest List Analysis ===")
    print("\nRestriction Summary:")
    for restriction, count in guest_analyzer.get_restriction_summary().items():
        print(f"- {restriction}: {count} people")
    
    print("\nTag Summary:")
    for tag, count in guest_analyzer.get_tag_summary().items():
        print(f"- {tag}: {count} people")
    
    print("\nRestriction Groups:")
    for restriction, names in guest_analyzer.get_restriction_groups().items():
        print(f"- {restriction}: {', '.join(names)}")
    
    # Create sample meals
    meals = create_sample_meals()
    
    # Analyze meal compatibility
    meal_analyzer = guest_analyzer.analyze_meal_compatibility(meals)
    
    # Print meal compatibility analysis
    print("\n=== Meal Compatibility Analysis ===")
    print("\nMost Compatible Meals:")
    print(meal_analyzer.get_most_compatible_meals().to_string(index=False))
    
    print("\nUniversally Compatible Meals:")
    print(meal_analyzer.get_universally_compatible_meals().to_string(index=False))
    
    print("\nCompatibility Matrix (with emojis):")
    print(meal_analyzer.get_compatibility_matrix(use_emojis=True).to_markdown(index=False))
    
    print("\nCompatibility Matrix (without emojis):")
    print(meal_analyzer.get_compatibility_matrix(use_emojis=False).to_markdown(index=False))
    

if __name__ == "__main__":
    main() 