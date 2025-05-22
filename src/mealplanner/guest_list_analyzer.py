import pandas as pd
from typing import List, Dict, Optional, Set
from .dietary_model import Person, DietaryRestriction, tag_registry, FoodCategory, Meal
from .natural_language_parsing import parse_nl_restriction, NO_RESTRICTION_PHRASES
from .meal_compatibility_analyzer import MealCompatibilityAnalyzer

class GuestListAnalyzer:
    """
    Analyzes a list of guests and their dietary restrictions to provide insights
    about the group's dietary needs and restrictions.
    """
    
    def __init__(self, guest_list: pd.DataFrame):
        """
        Initialize the analyzer with a guest list.
        
        Parameters
        ----------
        guest_list : pd.DataFrame
            DataFrame with at least 'Name' and 'Dietary Restriction' columns
        """
        self.guest_list = guest_list
        self.people: List[Person] = []
        self._parse_guests()
        
    def _parse_guests(self):
        """Parse the guest list into Person objects with dietary restrictions."""
        for _, row in self.guest_list.iterrows():
            name = row['Name']
            restriction_text = str(row['Dietary Restriction']).strip().lower()
            
            # Check if this is a "no restriction" phrase
            if restriction_text in NO_RESTRICTION_PHRASES:
                # Create a Person with no restrictions
                person = Person(name=name, restriction=DietaryRestriction(set()))
            else:
                # Parse the dietary restriction text
                restriction = parse_nl_restriction(restriction_text)
                if restriction is None:
                    # If parsing failed, treat as no restrictions
                    restriction = DietaryRestriction(set())
                person = Person(name=name, restriction=restriction)
            
            self.people.append(person)
    
    def _get_implied_tags(self, restriction: DietaryRestriction) -> set[str]:
        """Get the set of implied tags for a given restriction."""
        if not restriction or not restriction.excluded:
            return {"NO-RESTRICTIONS"}
        #TODO: This section needs to be changed, as this category match should not be hard-coded.
        tags = set()
        category_to_tags = {
            "ANIMAL_PRODUCTS": {"VEGAN", "DAIRY-FREE", "EGG-FREE", "MEAT-FREE", "FISH-FREE", "SHELLFISH-FREE"},
            "MEAT": {"VEGETARIAN"},
            "DAIRY": {"DAIRY-FREE"},
            "NUTS": {"NUT-FREE"},
            "SHELLFISH": {"SHELLFISH-FREE", "VEGETARIAN"}
        }
        for category in restriction.excluded:
            food_cat = FoodCategory.get(category)
            if food_cat and food_cat.name in category_to_tags:
                tags.update(category_to_tags[food_cat.name])
        return tags
    
    def get_restriction_summary(self) -> Dict[str, int]:
        """
        Get a summary of dietary restrictions in the group.
        
        Returns
        -------
        Dict[str, int]
            Dictionary mapping restriction types to count of people with that restriction
        """
        summary = {}
        for person in self.people:
            if person.restriction and person.restriction.excluded:
                # Get the string representation of the restriction
                restriction_str = str(person.restriction)
                summary[restriction_str] = summary.get(restriction_str, 0) + 1
            else:
                summary["No restrictions"] = summary.get("No restrictions", 0) + 1
        return summary
    
    def get_tag_summary(self) -> dict[str, int]:
        """Get a summary of dietary tags in the guest list."""
        summary = {}
        for person in self.people:
            tags = self._get_implied_tags(person.restriction)
            for tag in tags:
                if tag not in summary:
                    summary[tag] = 0
                summary[tag] += 1
        return summary
    
    def get_restriction_matrix(self, use_emojis: bool = False, categories: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Create a matrix showing which food categories each person can eat.
        True means they can eat it, False means they cannot.
        
        Parameters
        ----------
        use_emojis : bool, default=False
            Whether to use emoji checkmarks/crosses (✅/❌) instead of True/False
        categories : List[str], optional
            List of specific categories to show. If None, shows only categories
            that are relevant to the guest list (i.e., categories that are
            restricted by at least one person).
            
        Returns
        -------
        pd.DataFrame
            Matrix with people as rows and food categories as columns
        """
        # Get categories to show
        if categories is None:
            # Get categories that are relevant to the guest list
            relevant_categories = set()
            for person in self.people:
                if person.restriction and person.restriction.excluded:
                    relevant_categories.update(person.restriction.excluded)
            # Add parent categories of excluded categories
            for category in list(relevant_categories):
                cat = FoodCategory.get(category)
                if cat and cat.parents:
                    for p in cat.parents:
                        if hasattr(p, 'name'):
                            relevant_categories.add(p.name)
                        else:
                            relevant_categories.add(str(p))
            categories = sorted(relevant_categories)
        else:
            # Validate provided categories
            valid_categories = []
            for cat in categories:
                if FoodCategory.get(cat):
                    valid_categories.append(cat)
                else:
                    print(f"Warning: Unknown category '{cat}' will be ignored")
            categories = valid_categories
        
        # Create the matrix
        matrix_data = []
        for person in self.people:
            row = {"Name": person.name}
            for category in categories:
                food_cat = FoodCategory.get(category)
                can_eat = not person.restriction.forbids(food_cat) if person.restriction else True
                row[category] = "✅" if use_emojis and can_eat else "❌" if use_emojis else can_eat
            matrix_data.append(row)
        
        return pd.DataFrame(matrix_data)
    
    def get_common_restrictions(self, min_count: int = 2) -> Dict[str, int]:
        """
        Get food categories that are restricted by multiple people.
        
        Parameters
        ----------
        min_count : int
            Minimum number of people who must have a restriction for it to be included
            
        Returns
        -------
        Dict[str, int]
            Dictionary mapping food categories to count of people who restrict them
        """
        category_counts = {}
        for person in self.people:
            if person.restriction and person.restriction.excluded:
                for category in person.restriction.excluded:
                    category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            category: count 
            for category, count in category_counts.items() 
            if count >= min_count
        }
    
    def get_restriction_groups(self) -> Dict[str, List[str]]:
        """
        Group people by their dietary restrictions.
        
        Returns
        -------
        Dict[str, List[str]]
            Dictionary mapping restriction types to lists of names
        """
        groups = {}
        for person in self.people:
            if person.restriction and person.restriction.excluded:
                restriction_str = str(person.restriction)
            else:
                restriction_str = "No restrictions"
                
            if restriction_str not in groups:
                groups[restriction_str] = []
            groups[restriction_str].append(person.name)
            
        return groups
    
    def get_tag_groups(self) -> Dict[str, List[str]]:
        """
        Group people by their canonical dietary tags.
        
        Returns
        -------
        Dict[str, List[str]]
            Dictionary mapping tag names to lists of names
        """
        groups = {}
        for person in self.people:
            tags = self._get_implied_tags(person.restriction)
            for tag in tags:
                if tag not in groups:
                    groups[tag] = []
                groups[tag].append(person.name)
        return groups

    def analyze_meal_compatibility(self, meals: List[Meal]) -> MealCompatibilityAnalyzer:
        """
        Create a MealCompatibilityAnalyzer for the guest list.
        
        Parameters
        ----------
        meals : List[Meal]
            List of meals to analyze for compatibility
            
        Returns
        -------
        MealCompatibilityAnalyzer
            Analyzer object for meal compatibility with this guest list
        """
        return MealCompatibilityAnalyzer(meals, self.people)

def analyze_guest_list(guest_list: pd.DataFrame) -> GuestListAnalyzer:
    """
    Create a GuestListAnalyzer from a guest list DataFrame.
    
    Parameters
    ----------
    guest_list : pd.DataFrame
        DataFrame with at least 'Name' and 'Dietary Restriction' columns
        
    Returns
    -------
    GuestListAnalyzer
        Analyzer object for the guest list
    """
    return GuestListAnalyzer(guest_list) 