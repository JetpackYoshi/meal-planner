from restrictions import DietaryRestriction

class TagRegistry:
    def __init__(self):
        self._tag_map: dict[str, DietaryRestriction] = {}

    def register_tag(self, tag_name: str, restriction: DietaryRestriction):
        self._tag_map[tag_name.upper()] = restriction

    def get_tag(self, tag_name: str) -> DietaryRestriction:
        return self._tag_map[tag_name.upper()]

    def generate_tags(self, restriction: DietaryRestriction) -> list[str]:
        # Try to find an exact match
        for tag, known_restriction in self._tag_map.items():
            if restriction.excluded == known_restriction.excluded:
                return [tag]

        # Fallback to individual "-FREE" labels
        return [f"{item}-FREE" for item in sorted(restriction.excluded)]

    def all_tags(self) -> list[str]:
        return list(self._tag_map.keys())


# Global registry
tag_registry = TagRegistry()

# Canonical definitions
tag_registry.register_tag("VEGAN", DietaryRestriction({"ANIMAL_PRODUCTS"}))
tag_registry.register_tag("VEGETARIAN", DietaryRestriction({"MEAT", "FISH", "SHELLFISH"}))
tag_registry.register_tag("PESCATARIAN", DietaryRestriction({"MEAT"}))