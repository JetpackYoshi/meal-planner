"""
Default food categories and dietary tags for the meal planner.

This module provides a centralized place for defining commonly used food categories
and dietary tags. Users can import these defaults and extend or override them as needed.
"""

from .dietary_model import FoodCategory, DietaryRestriction, tag_registry

def setup_default_food_categories():
    """Sets up the default food category hierarchy."""
    FoodCategory.reset()
    
    # Base categories
    FoodCategory.define("ANIMAL_PRODUCTS")
    FoodCategory.define("PLANT_BASED")
    
    # Animal product subcategories
    FoodCategory.define("MEAT", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("DAIRY", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("EGGS", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("FISH", {"ANIMAL_PRODUCTS"})
    FoodCategory.define("SHELLFISH", {"FISH"})  # SHELLFISH is a subcategory of FISH
    
    # Meat subcategories
    FoodCategory.define("BEEF", {"MEAT"})
    FoodCategory.define("CHICKEN", {"MEAT"})
    FoodCategory.define("PORK", {"MEAT"})
    
    # Dairy subcategories
    FoodCategory.define("CHEESE", {"DAIRY"})
    FoodCategory.define("MILK", {"DAIRY"})
    FoodCategory.define("YOGURT", {"DAIRY"})
    
    # Fish subcategories
    FoodCategory.define("SALMON", {"FISH"})
    FoodCategory.define("TUNA", {"FISH"})
    
    # Plant-based categories
    FoodCategory.define("NUTS", {"PLANT_BASED"})
    FoodCategory.define("GRAINS", {"PLANT_BASED"})
    FoodCategory.define("LEGUMES", {"PLANT_BASED"})
    FoodCategory.define("VEGETABLES", {"PLANT_BASED"})
    FoodCategory.define("FRUITS", {"PLANT_BASED"})
    
    # Nut subcategories
    FoodCategory.define("ALMOND", {"NUTS"})
    FoodCategory.define("PEANUT", {"NUTS"})
    FoodCategory.define("CASHEW", {"NUTS"})
    
    # Grain subcategories
    FoodCategory.define("WHEAT", {"GRAINS"})
    FoodCategory.define("RICE", {"GRAINS"})
    FoodCategory.define("OATS", {"GRAINS"})
    
    # Common allergens
    FoodCategory.define("GLUTEN", {"WHEAT"})
    FoodCategory.define("SOY", {"LEGUMES"})
    
    # Plant-based subcategories
    FoodCategory.define("TOFU", {"SOY"})
    
    # Cuisine categories
    FoodCategory.define("CUISINE")
    FoodCategory.define("ASIAN", {"CUISINE"})
    FoodCategory.define("JAPANESE", {"ASIAN"})
    FoodCategory.define("CHINESE", {"ASIAN"})
    FoodCategory.define("ITALIAN", {"CUISINE"})
    FoodCategory.define("MEXICAN", {"CUISINE"})

def setup_default_tags():
    """Sets up the default dietary tags."""
    tag_registry.clear()
    
    # Ethical dietary tags
    tag_registry.register_tag("VEGAN", DietaryRestriction({"ANIMAL_PRODUCTS"}), category="ethical")
    tag_registry.register_tag("VEGETARIAN", DietaryRestriction({"MEAT", "FISH", "SHELLFISH"}), category="ethical")
    tag_registry.register_tag("PESCATARIAN", DietaryRestriction({"MEAT"}), category="ethical")
    tag_registry.register_tag("MEAT-FREE", DietaryRestriction({"MEAT"}), category="ethical")
    
    # Allergen tags
    tag_registry.register_tag("NUT-FREE", DietaryRestriction({"NUTS"}), category="allergen")
    tag_registry.register_tag("DAIRY-FREE", DietaryRestriction({"DAIRY"}), category="allergen")
    tag_registry.register_tag("EGG-FREE", DietaryRestriction({"EGGS"}), category="allergen")
    tag_registry.register_tag("SHELLFISH-FREE", DietaryRestriction({"SHELLFISH"}), category="allergen")
    tag_registry.register_tag("FISH-FREE", DietaryRestriction({"FISH"}), category="allergen")
    tag_registry.register_tag("BEEF-FREE", DietaryRestriction({"BEEF"}), category="allergen")
    tag_registry.register_tag("GLUTEN-FREE", DietaryRestriction({"GLUTEN"}), category="allergen")
    tag_registry.register_tag("SOY-FREE", DietaryRestriction({"SOY"}), category="allergen")

def setup_defaults():
    """Sets up all default categories and tags."""
    setup_default_food_categories()
    setup_default_tags() 