import pandas as pd
from collections import OrderedDict
from typing import Literal
import logging

# ------------------------------
# FoodCategory
# ------------------------------
class FoodCategory:
    """
    Represents a hierarchical food category.

    Each category may have parent categories (e.g., CHEESE → DAIRY → ANIMAL_PRODUCTS)
    and children, allowing dynamic nesting and inheritance.
    """
    _registry: dict[str, 'FoodCategory'] = {}

    def __init__(self, name: str):
        """
        Parameters
        ----------
        name : str
            The name of the food category (e.g., "DAIRY", "MEAT")
        """
        self.name: str = name.upper()
        self.parents: set[str] = set()
        self.children: set[str] = set()
        FoodCategory._registry[self.name] = self

    def add_parent(self, parent_name: str):
        """Adds a parent category by name."""
        parent_name = parent_name.upper()
        self.parents.add(parent_name)
        parent = FoodCategory._registry.get(parent_name)
        if parent:
            parent.children.add(self.name)
        else:
            raise ValueError(f"Parent category '{parent_name}' is not defined.")

    def ancestors(self) -> set[str]:
        """Returns the set of all ancestors of this category."""
        result = set(self.parents)
        for parent in self.parents:
            result |= FoodCategory.get(parent).ancestors()
        return result

    def is_a(self, category_name: str) -> bool:
        """
        Checks whether this category is a (direct or indirect) subtype of the given category.

        Parameters
        ----------
        category_name : str
            The name of the parent category to check.

        Returns
        -------
        bool
            True if this category is or inherits from `category_name`.
        """
        category_name = category_name.upper()
        return category_name == self.name or category_name in self.ancestors()

    def __repr__(self) -> str:
        return f"FoodCategory({self.name})"

    @classmethod
    def define(cls, name: str, parents: set[str] = None) -> 'FoodCategory':
        """Defines a new FoodCategory with optional parent categories."""
        obj = cls._registry.get(name.upper())
        if not obj:
            obj = cls(name)
        if parents:
            for parent in parents:
                obj.add_parent(parent)
        return obj

    @classmethod
    def get(cls, name: str) -> 'FoodCategory':
        """Retrieves a defined FoodCategory by name."""
        return cls._registry[name.upper()]

    @classmethod
    def all(cls) -> list['FoodCategory']:
        """Returns a list of all defined food categories."""
        return list(cls._registry.values())

    @classmethod
    def reset(cls):
        """Clears the category registry (useful for testing)."""
        cls._registry = {}

# ------------------------------
# DietaryRestriction
# ------------------------------
class DietaryRestriction:
    """
    Represents a dietary restriction by listing excluded food categories.
    """
    def __init__(self, excluded: set[str]):
        """
        Parameters
        ----------
        excluded : set of str
            The set of excluded food categories (e.g., {"MEAT", "DAIRY"}).
        """
        self.excluded: set[str] = {name.upper() for name in excluded}

    def forbids(self, food: FoodCategory) -> bool:
        """
        Returns True if the food category is forbidden by this restriction.
        """
        return any(food.is_a(excluded) for excluded in self.excluded)

    def is_compatible_with(self, ingredients: list[FoodCategory]) -> bool:
        """
        Returns True if all the given food categories are allowed.
        """
        return all(not self.forbids(item) for item in ingredients)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(Excludes: {sorted(self.excluded)})"

# ------------------------------
# Ingredient
# ------------------------------
class Ingredient:
    """
    Represents a specific ingredient with metadata.
    """
    def __init__(self, name: str, category: FoodCategory, calories: float = 0.0, allergens: set[str] = None):
        """
        Parameters
        ----------
        name : str
            The name of the ingredient (e.g., "Cheddar Cheese")
        category : FoodCategory
            The food category it belongs to (e.g., CHEESE)
        calories : float
            Caloric content
        allergens : set of str, optional
            Allergen labels (e.g., {"milk"})
        """
        self.name = name
        self.category = category
        self.calories = calories
        self.allergens = allergens or set()

    def __repr__(self) -> str:
        allergen_info = f" (Allergens: {', '.join(self.allergens)})" if self.allergens else ""
        return f"{self.name} [{self.category.name}] - {self.calories} kcal{allergen_info}"

class Meal:
    """
    Represents a meal composed of multiple ingredients.
    """
    def __init__(self, name: str, ingredients: list[Ingredient]):
        self.name = name
        self.ingredients = ingredients

    def categories(self) -> set[str]:
        """Returns the set of all food categories (and their ancestors) used in the meal."""
        all_categories = set()
        for ingredient in self.ingredients:
            cat = ingredient.category
            all_categories.add(cat.name)
            all_categories |= cat.ancestors()
        return all_categories

    def is_compatible_with(self, restriction: DietaryRestriction) -> bool:
        """Checks if this meal is compatible with a given dietary restriction."""
        return restriction.is_compatible_with([ing.category for ing in self.ingredients])

    def is_compatible_with_group(self, restrictions: list[DietaryRestriction]) -> bool:
        """Checks if this meal is compatible with all restrictions in a group."""
        return all(self.is_compatible_with(r) for r in restrictions)

    def total_calories(self) -> float:
        """Returns the total number of calories in the meal."""
        return sum(ing.calories for ing in self.ingredients)

    def __repr__(self) -> str:
        return f"Meal({self.name}, {len(self.ingredients)} items, {self.total_calories():.1f} kcal)"


# ------------------------------
# Utility: categorize_from_string
# ------------------------------
def categorize_from_string(ingredient_name: str) -> FoodCategory:
    """
    Attempts to categorize an ingredient name by matching it to known food category names.

    Parameters
    ----------
    ingredient_name : str
        The name of the ingredient to categorize (e.g., "chicken breast")

    Returns
    -------
    FoodCategory
        The matching food category

    Raises
    ------
    ValueError
        If no category match is found.
        
    Examples
    --------
    >>> categorize_from_string("roast beef")
    FoodCategory('BEEF')
    >>> categorize_from_string("cheddar cheese")
    FoodCategory('CHEESE')
    """
    name = ingredient_name.strip().upper()
    for category in FoodCategory.all():
        if category.name in name:
            return category
    raise ValueError(f"No matching category found for '{ingredient_name}'")


class Tag:
    def __init__(self, name: str, restriction: DietaryRestriction, category: str = "unspecified"):
        self.name = name.upper()
        self.restriction = restriction
        self.category = category.lower()

    def __repr__(self):
        return f"Tag({self.name}, category={self.category})"

# ------------------------------
# TagRegistry
# ------------------------------
class TagRegistry:
    """
    Registry for dietary tags and their associated restrictions.
    """
    def __init__(self):
        self._tag_map: dict[str, DietaryRestriction] = {}
        self._tag_categories: dict[str, str] = {}

    def register_tag(self, tag_name: str, restriction: DietaryRestriction, category: str = "unspecified", *, overwrite: bool = False):
        """Registers a new dietary tag with its associated restriction."""
        if tag_name in self._tag_map and not overwrite:
            raise ValueError(f"Tag '{tag_name}' already exists. Use overwrite=True to replace it.")
        self._tag_map[tag_name] = restriction
        self._tag_categories[tag_name] = category

    def get_tag(self, tag_name: str) -> DietaryRestriction:
        """Retrieves the restriction associated with a tag."""
        return self._tag_map[tag_name]

    def get_implied_tags(self, restriction: DietaryRestriction) -> set[str]:
        """
        Get the set of tags implied by a dietary restriction.
        This is determined by checking which registered tags' restrictions
        are satisfied by the given restriction, taking into account the
        hierarchical relationships between food categories.
        
        Parameters
        ----------
        restriction : DietaryRestriction
            The restriction to check for implied tags
            
        Returns
        -------
        set[str]
            Set of tag names that are implied by the restriction
        """
        if not restriction or not restriction.excluded:
            return {"NO-RESTRICTIONS"}
            
        implied_tags = set()
        for tag_name, tag_restriction in self._tag_map.items():
            # A tag is implied if all categories in its restriction are excluded
            # or if their parent categories are excluded
            if all(
                any(
                    FoodCategory.get(cat).is_a(excluded_cat)
                    for excluded_cat in restriction.excluded
                )
                for cat in tag_restriction.excluded
            ):
                implied_tags.add(tag_name)
        return implied_tags

    def generate_tags(self, restriction: DietaryRestriction) -> list[str]:
        """Generates appropriate tags for a given restriction."""
        return list(self.get_implied_tags(restriction))

    def get_all_implied_tags(self, restriction: DietaryRestriction) -> list[str]:
        """Gets all tags implied by a restriction, including those from parent categories."""
        return list(self.get_implied_tags(restriction))

    def all_tags(self) -> list[str]:
        """Returns a list of all registered tag names."""
        return list(self._tag_map.keys())

    def get_tags_by_category(self, category: str) -> list[str]:
        """Returns a list of tag names in the specified category."""
        return [tag for tag, cat in self._tag_categories.items() if cat == category.lower()]

    def clear(self):
        """Clears all registered tags."""
        self._tag_map.clear()
        self._tag_categories.clear()

# Create a global tag registry
tag_registry = TagRegistry()

# ------------------------------
# Person
# ------------------------------
class Person:
    """
    Represents a person with dietary restrictions.
    """
    def __init__(self, name: str, restriction: DietaryRestriction = None, tag: str = None):
        """
        Parameters
        ----------
        name : str
            The person's name
        restriction : DietaryRestriction, optional
            The person's dietary restrictions
        tag : str, optional
            A canonical dietary tag (e.g., "VEGAN", "VEGETARIAN")
        """
        self.name = name
        if tag:
            self.restriction = tag_registry.get_tag(tag)
        else:
            self.restriction = restriction or DietaryRestriction(set())

    def label(self) -> str:
        """Get a human-readable label for the person's dietary restrictions."""
        if not self.restriction or not self.restriction.excluded:
            return "No restrictions"
        return str(self.restriction)

    def __repr__(self):
        return f"Person({self.name}, {self.label()})"


if __name__ == '__main__':
   pass