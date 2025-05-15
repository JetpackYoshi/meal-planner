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




if __name__ == '__main__':
   pass