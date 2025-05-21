import pandas as pd
from typing import List, Dict, Optional, Set
from .dietary_model import Person, DietaryRestriction, tag_registry
from .natural_language_parsing import parse_nl_restriction, NO_RESTRICTION_PHRASES

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
    
    def _get_implied_tags(self, restriction: DietaryRestriction) -> Set[str]:
        """
        Get all tags that apply to a restriction, including implied ones.
        
        Parameters
        ----------
        restriction : DietaryRestriction
            The restriction to analyze
            
        Returns
        -------
        Set[str]
            Set of all applicable tags
        """
        if not restriction or not restriction.excluded:
            return {"NO-RESTRICTIONS"}
            
        # Get base tags
        tags = set(tag_registry.generate_tags(restriction))
        
        # Add implied tags based on restrictions
        if "ANIMAL_PRODUCTS" in restriction.excluded:
            # Vegan implies no animal products at all
            tags.update({
                "DAIRY-FREE", "EGG-FREE", "MEAT-FREE", 
                "FISH-FREE", "SHELLFISH-FREE", "BEEF-FREE"
            })
            # Also add the actual exclusions
            restriction.excluded.update({
                "MEAT", "FISH", "SHELLFISH", "DAIRY", "EGGS", "BEEF"
            })
        if "MEAT" in restriction.excluded:
            tags.add("MEAT-FREE")
        if "FISH" in restriction.excluded:
            tags.add("FISH-FREE")
        if "SHELLFISH" in restriction.excluded:
            tags.add("SHELLFISH-FREE")
        if "DAIRY" in restriction.excluded:
            tags.add("DAIRY-FREE")
        if "EGGS" in restriction.excluded:
            tags.add("EGG-FREE")
        if "NUTS" in restriction.excluded:
            tags.add("NUT-FREE")
        if "BEEF" in restriction.excluded:
            tags.add("BEEF-FREE")
        
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
    
    def get_tag_summary(self) -> Dict[str, int]:
        """
        Get a summary of canonical dietary tags in the group.
        
        Returns
        -------
        Dict[str, int]
            Dictionary mapping tag names to count of people with that tag
        """
        tag_counts = {}
        for person in self.people:
            tags = self._get_implied_tags(person.restriction)
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts
    
    def get_restriction_matrix(self, use_emojis: bool = False) -> pd.DataFrame:
        """
        Create a matrix showing which food categories each person can eat.
        True means they can eat it, False means they cannot.
        
        Parameters
        ----------
        use_emojis : bool
            If True, use ✅/❌ instead of True/False in the output
            
        Returns
        -------
        pd.DataFrame
            Matrix with people as rows and food categories as columns
        """
        # Get all unique food categories from restrictions
        all_categories = set()
        for person in self.people:
            if person.restriction and person.restriction.excluded:
                all_categories.update(person.restriction.excluded)
        
        # Create the matrix
        matrix_data = []
        for person in self.people:
            row = {"Name": person.name}
            for category in sorted(all_categories):
                # If no restrictions or category not in restrictions, they can eat it
                can_eat = (
                    not person.restriction or 
                    not person.restriction.excluded or
                    category not in person.restriction.excluded
                )
                row[category] = "✅" if can_eat else "❌" if use_emojis else can_eat
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