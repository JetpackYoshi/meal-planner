import pandas as pd
from collections import OrderedDict
from typing import Literal

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
    Registry to manage canonical dietary tags.
    Tags are prioritized by registration order.
    """
    def __init__(self):
        self._tag_map: OrderedDict[str, Tag] = OrderedDict()

    def register_tag(self, tag_name: str, restriction: DietaryRestriction, category: str = "unspecified", *, overwrite: bool = False):
        tag_name = tag_name.upper()
        if tag_name in self._tag_map and not overwrite:
            raise ValueError(f"Tag '{tag_name}' already registered.")
        self._tag_map[tag_name] = Tag(tag_name, restriction, category)

    def get_tag(self, tag_name: str) -> DietaryRestriction:
        return self._tag_map[tag_name.upper()].restriction

    def generate_tags(self, restriction: DietaryRestriction) -> list[str]:
        """
        Generates a list of canonical tags that describe the restriction.
        Uses exact match or greedy subset cover.

        Parameters
        ----------
        restriction : DietaryRestriction
            The restriction to evaluate against known tags.

        Returns
        -------
        list of str
            The best-fitting tags to describe the restriction.
        """
        normalized = restriction.excluded

        # Exact match
        for tag in self._tag_map.values():
            if normalized == tag.restriction.excluded:
                return [tag.name]

        # Greedy subset match
        candidates = []
        for tag in self._tag_map.values():
            if tag.restriction.excluded.issubset(normalized):
                candidates.append((tag.name, tag.restriction.excluded))

        result = []
        remaining = set(normalized)
        for name, excluded in sorted(candidates, key=lambda x: -len(x[1])):
            if not excluded <= remaining:
                continue
            result.append(name)
            remaining -= excluded
            if not remaining:
                break

        if remaining:
            result.extend(f"{x}-FREE" for x in sorted(remaining))

        return result

    def all_tags(self) -> list[str]:
        return list(self._tag_map.keys())
    
    def get_tags_by_category(self, category: str) -> list[str]:
        """
        Returns a list of tag names matching the specified category.

        Parameters
        ----------
        category : str
            The category label to filter by (e.g., "ethical", "allergen")

        Returns
        -------
        list of str
            Tag names in the given category
        """
        return [tag.name for tag in self._tag_map.values() if tag.category == category.lower()]

# Global registry
tag_registry = TagRegistry()

# ------------------------------
# Person
# ------------------------------
class Person:
    """
    Represents a person and their dietary restriction, either by tag or custom restriction.
    """
    def __init__(self, name: str, restriction: DietaryRestriction = None, tag: str = None):
        """
        Parameters
        ----------
        name : str
            Person's name
        restriction : DietaryRestriction, optional
            Directly defined restriction
        tag : str, optional
            Predefined dietary tag (e.g., "VEGAN")
        """
        self.name = name

        if restriction:
            self.restriction = restriction
        elif tag:
            self.restriction = tag_registry.get_tag(tag)
        else:
            raise ValueError("Must provide either a restriction or a tag.")

    def label(self) -> str:
        """Returns a string with the person's name and canonical dietary tags."""
        tags = tag_registry.generate_tags(self.restriction)
        return f"{self.name} [{' | '.join(tags)}]"

    def __repr__(self):
        return self.label()


class MealCompatibilityAnalyzer:
    def __init__(self, meals: list[Meal], people: list[Person]):
        self.meals = meals
        self.people = people
        self._matrix: pd.DataFrame | None = None

    def build_matrix(self) -> pd.DataFrame:
        """
        Builds the compatibility matrix where each cell indicates whether a meal
        is compatible with a person.

        Returns
        -------
        pd.DataFrame
            The compatibility matrix
        """
        data = {
            person.label(): [
                meal.is_compatible_with(person.restriction) for meal in self.meals
            ] for person in self.people
        }
        self._matrix = pd.DataFrame(data, index=[meal.name for meal in self.meals])
        return self._matrix
    
    def score_meals(self) -> pd.Series:
        """Returns a Series with the number of people compatible with each meal."""
        matrix = self.get_matrix()
        return matrix.sum(axis=1)  # Sum True values across each row

    def get_most_compatible_meals(self, top_n: int | None = None) -> pd.DataFrame:
        """Returns a DataFrame of meals sorted by descending compatibility count."""
        matrix = self.get_matrix()
        scores = self.score_meals()
        sorted_df = matrix.assign(Compatible_Count=scores).sort_values(
            "Compatible_Count", ascending=False
        )
        if top_n:
            return sorted_df.head(top_n)
        return sorted_df

    def get_universally_compatible_meals(self) -> pd.DataFrame:
        """Returns meals compatible with all people."""
        matrix = self.get_matrix()
        return matrix[matrix.all(axis=1)]


    def get_matrix(self) -> pd.DataFrame:
        """Returns the compatibility matrix, building it if necessary."""
        if self._matrix is None:
            return self.build_matrix()
        return self._matrix

    def print_matrix(self, mode: Literal["plain", "markdown"] = "plain"):
        """
        Prints the compatibility matrix in either plain or markdown format.

        Parameters
        ----------
        mode : {'plain', 'markdown'}
            Output format
        """
        df = self.get_matrix()
        df_display = df.map(lambda val: "✅" if val else "❌")

        if mode == "plain":
            print(df_display)
        elif mode == "markdown":
            print(df_display.to_markdown())
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    def export_csv(self, path: str):
        """Exports the compatibility matrix to a CSV file."""
        self.get_matrix().to_csv(path, index=True)

    def export_markdown(self, path: str):
        """Exports the compatibility matrix to a markdown-formatted .md file."""
        df_display = self.get_matrix().applymap(lambda val: "✅" if val else "❌")
        with open(path, "w") as f:
            f.write(df_display.to_markdown())


if __name__ == '__main__':
   pass