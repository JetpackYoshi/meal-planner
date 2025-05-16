import pandas as pd
from collections import OrderedDict
from typing import Literal

class FoodCategory:
    _registry: dict[str, 'FoodCategory'] = {}

    def __init__(self, name: str):
        self.name: str = name.upper()
        self.parents: set[str] = set()
        self.children: set[str] = set()
        FoodCategory._registry[self.name] = self

    def add_parent(self, parent_name: str):
        parent_name = parent_name.upper()
        self.parents.add(parent_name)
        parent = FoodCategory._registry.get(parent_name)
        if parent:
            parent.children.add(self.name)
        else:
            raise ValueError(f"Parent category '{parent_name}' is not defined.")

    def ancestors(self) -> set[str]:
        result = set(self.parents)
        for parent in self.parents:
            result |= FoodCategory.get(parent).ancestors()
        return result

    def is_a(self, category_name: str) -> bool:
        category_name = category_name.upper()
        return category_name == self.name or category_name in self.ancestors()

    def __repr__(self) -> str:
        return f"FoodCategory({self.name})"

    @classmethod
    def define(cls, name: str, parents: set[str] = None) -> 'FoodCategory':
        obj = cls._registry.get(name.upper())
        if not obj:
            obj = cls(name)
        if parents:
            for parent in parents:
                obj.add_parent(parent)
        return obj

    @classmethod
    def get(cls, name: str) -> 'FoodCategory':
        return cls._registry[name.upper()]

    @classmethod
    def all(cls) -> list['FoodCategory']:
        return list(cls._registry.values())

    @classmethod
    def reset(cls):
        cls._registry = {}

class DietaryRestriction:
    def __init__(self, excluded: set[str]):
        self.excluded: set[str] = {name.upper() for name in excluded}

    def forbids(self, food: FoodCategory) -> bool:
        return any(food.is_a(excluded) for excluded in self.excluded)

    def is_compatible_with(self, ingredients: list[FoodCategory]) -> bool:
        return all(not self.forbids(item) for item in ingredients)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(Excludes: {sorted(self.excluded)})"

class Ingredient:
    def __init__(self, name: str, category: FoodCategory, calories: float = 0.0, allergens: set[str] = None):
        self.name = name
        self.category = category
        self.calories = calories
        self.allergens = allergens or set()

    def __repr__(self) -> str:
        allergen_info = f" (Allergens: {', '.join(self.allergens)})" if self.allergens else ""
        return f"{self.name} [{self.category.name}] - {self.calories} kcal{allergen_info}"

class Meal:
    def __init__(self, name: str, ingredients: list[Ingredient]):
        self.name = name
        self.ingredients = ingredients

    def categories(self) -> set[str]:
        all_categories = set()
        for ingredient in self.ingredients:
            cat = ingredient.category
            all_categories.add(cat.name)
            all_categories |= cat.ancestors()
        return all_categories

    def is_compatible_with(self, restriction: DietaryRestriction) -> bool:
        return restriction.is_compatible_with([ing.category for ing in self.ingredients])

    def is_compatible_with_group(self, restrictions: list[DietaryRestriction]) -> bool:
        return all(self.is_compatible_with(r) for r in restrictions)

    def total_calories(self) -> float:
        return sum(ing.calories for ing in self.ingredients)

    def __repr__(self) -> str:
        return f"Meal({self.name}, {len(self.ingredients)} items, {self.total_calories():.1f} kcal)"


def categorize_from_string(ingredient_name: str) -> FoodCategory:
    name = ingredient_name.strip().upper()
    for category in FoodCategory.all():
        if category.name in name:
            return category
    raise ValueError(f"No matching category found for '{ingredient_name}'")

class TagRegistry:
    def __init__(self):
        # Order = priority (first match wins)
        self._tag_map: OrderedDict[str, DietaryRestriction] = OrderedDict()

    def register_tag(self, tag_name: str, restriction: DietaryRestriction, *, overwrite: bool = False):
        tag_name = tag_name.upper()
        if tag_name in self._tag_map and not overwrite:
            raise ValueError(f"Tag '{tag_name}' already registered.")
        self._tag_map[tag_name] = restriction

    def get_tag(self, tag_name: str) -> DietaryRestriction:
        return self._tag_map[tag_name.upper()]

    def generate_tags(self, restriction: DietaryRestriction) -> list[str]:
        normalized = restriction.excluded

        # First: exact match
        for tag, known in self._tag_map.items():
            if normalized == known.excluded:
                return [tag]

        # Step 1: Gather subset-match candidates
        candidates = []
        for tag, known in self._tag_map.items():
            if known.excluded.issubset(normalized):
                candidates.append((tag, known.excluded))

        # Step 2: Greedy cover — prefer largest unique matches first
        used = set()
        result = []
        remaining = set(normalized)

        for tag, excluded in sorted(candidates, key=lambda x: -len(x[1])):
            if not excluded <= remaining:
                continue
            result.append(tag)
            remaining -= excluded
            if not remaining:
                break

        # Step 3: Fallback if any exclusions remain
        if remaining:
            result.extend(f"{x}-FREE" for x in sorted(remaining))

        return result


    def all_tags(self) -> list[str]:
        return list(self._tag_map.keys())

# Global registry
tag_registry = TagRegistry()

class Person:
    def __init__(self, name: str, restriction: DietaryRestriction = None, tag: str = None):
        self.name = name

        if restriction:
            self.restriction = restriction
        elif tag:
            self.restriction = tag_registry.get_tag(tag)
        else:
            raise ValueError("Must provide either a restriction or a tag.")

    def label(self) -> str:
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
        """Build and store the compatibility matrix as a pandas DataFrame."""
        data = {
            person.label(): [
                meal.is_compatible_with(person.restriction) for meal in self.meals
            ]
            for person in self.people
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
        """Returns the matrix, building it if needed."""
        if self._matrix is None:
            return self.build_matrix()
        return self._matrix

    def print_matrix(
        self, mode: Literal["plain", "markdown"] = "plain"
    ):
        df = self.get_matrix()
        df_display = df.map(lambda val: "✅" if val else "❌")

        if mode == "plain":
            print(df_display)
        elif mode == "markdown":
            print(df_display.to_markdown())
        else:
            raise ValueError(f"Unsupported mode: {mode}")

    def export_csv(self, path: str):
        self.get_matrix().to_csv(path, index=True)

    def export_markdown(self, path: str):
        df_display = self.get_matrix().applymap(lambda val: "✅" if val else "❌")
        with open(path, "w") as f:
            f.write(df_display.to_markdown())


if __name__ == '__main__':
   pass