class FoodCategory:
    """Defines A food category"""
    _registry = {}

    def __init__(self, name: str, parents: set[str] = None):
        self.name = name.upper()
        self.parents = set(parents) if parents else set()
        FoodCategory._registry[self.name] = self

    def ancestors(self) -> set[str]:
        '''Recursively find all parent categories'''
        result = set(self.parents)
        for parent in self.parents:
            result |= FoodCategory._registry[parent].ancestors()
        return result

    def is_a(self, category_name: str) -> bool:
        category_name = category_name.upper()
        return category_name == self.name or category_name in self.ancestors()

    def __repr__(self):
        return f"FoodCategory({self.name})"

    @classmethod
    def get(cls, name: str) -> 'FoodCategory':
        return cls._registry[name.upper()]

    @classmethod
    def all(cls) -> list:
        return list(cls._registry.values())

class DietaryRestriction:
    def __init__(self, excluded: set[str]):
        self.excluded = {name.upper() for name in excluded}

    def forbids(self, food: FoodCategory) -> bool:
        return any(food.is_a(forbidden) for forbidden in self.excluded)

    def is_compatible_with(self, ingredients: list[FoodCategory]) -> bool:
        return all(not self.forbids(item) for item in ingredients)

    def __repr__(self):
        return f"{self.__class__.__name__}(Excludes: {sorted(self.excluded)})"


if __name__ == '__main__':
   pass