from collections import OrderedDict
from restrictions import DietaryRestriction

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
        for tag, known in self._tag_map.items():
            if restriction.excluded == known.excluded:
                return [tag]  # First exact match wins
        return [f"{cat}-FREE" for cat in sorted(restriction.excluded)]

    def all_tags(self) -> list[str]:
        return list(self._tag_map.keys())


# Global registry
tag_registry = TagRegistry()

# Canonical definitions
# Register tags in priority order (most specific to least specific)
tag_registry.register_tag("VEGAN", DietaryRestriction({"ANIMAL_PRODUCTS"}))
tag_registry.register_tag("VEGETARIAN", DietaryRestriction({"MEAT", "FISH", "SHELLFISH"}))
tag_registry.register_tag("PESCATARIAN", DietaryRestriction({"MEAT"}))
