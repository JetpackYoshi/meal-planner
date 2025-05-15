class TagRegistry:
    def __init__(self):
        self._tag_map: dict[str, set[str]] = {}

    def register_tag(self, name: str, excluded_categories: set[str]):
        self._tag_map[name.upper()] = {x.upper() for x in excluded_categories}

    def generate_tags(self, excluded: set[str]) -> list[str]:
        normalized = set(x.upper() for x in excluded)

        # Exact matches first
        for tag, required_exclusions in self._tag_map.items():
            if normalized == required_exclusions:
                return [tag]

        # Fallback: individual tags
        return [f"{x}-FREE" for x in sorted(normalized)]

    def all_tags(self) -> dict[str, set[str]]:
        return dict(self._tag_map)

# Global registry
tag_registry = TagRegistry()

# Canonical definitions
tag_registry.register_tag("VEGAN", {"ANIMAL_PRODUCTS"})
tag_registry.register_tag("VEGETARIAN", {"MEAT", "FISH", "SHELLFISH"})
tag_registry.register_tag("PESCATARIAN", {"MEAT"})