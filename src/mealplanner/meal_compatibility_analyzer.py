import pandas as pd
from typing import List, Optional, Literal
from .dietary_model import Meal, Person, DietaryRestriction

class MealCompatibilityAnalyzer:
    """
    Analyzes the compatibility of meals with a group of people's dietary restrictions.
    Provides methods to score meals, find universally compatible meals, and generate
    compatibility matrices.
    """
    
    def __init__(self, meals: List[Meal], people: List[Person]):
        """
        Initialize the analyzer with a list of meals and people.
        
        Parameters
        ----------
        meals : List[Meal]
            List of meals to analyze
        people : List[Person]
            List of people to check compatibility against
        """
        self.meals = meals
        self.people = people
        
    def get_compatibility_matrix(self, use_emojis: bool = False) -> pd.DataFrame:
        """
        Create a matrix showing which meals each person can eat.
        True means they can eat it, False means they cannot.
        
        Parameters
        ----------
        use_emojis : bool, default=False
            Whether to use emoji checkmarks/crosses (✅/❌) instead of True/False
            
        Returns
        -------
        pd.DataFrame
            Matrix with meals as rows and people as columns
        """
        matrix_data = []
        for meal in self.meals:
            row = {"Meal": meal.name}
            for person in self.people:
                can_eat = meal.is_compatible_with(person.restriction)
                row[person.name] = "✅" if use_emojis and can_eat else "❌" if use_emojis else can_eat
            matrix_data.append(row)
        
        return pd.DataFrame(matrix_data)
    
    def score_meals(self) -> pd.Series:
        """
        Scores each meal based on how many people can eat it.
        
        Returns
        -------
        pd.Series
            Series mapping meal names to their compatibility scores
        """
        matrix = self.get_compatibility_matrix()
        
        # Calculate score as percentage of people who can eat each meal
        scores = matrix.drop('Meal', axis=1).mean(axis=1)
        scores.index = matrix['Meal']
        return scores
    
    def get_most_compatible_meals(self, top_n: Optional[int] = None) -> pd.DataFrame:
        """
        Get the most compatible meals, optionally limited to top N.
        
        Parameters
        ----------
        top_n : int, optional
            Number of top meals to return. If None, returns all meals.
            
        Returns
        -------
        pd.DataFrame
            DataFrame of meals sorted by compatibility score
        """
        scores = self.score_meals()
        result = pd.DataFrame({
            'Meal': scores.index,
            'Compatibility Score': scores.values
        })
        result = result.sort_values('Compatibility Score', ascending=False)
        
        if top_n is not None:
            result = result.head(top_n)
            
        return result
    
    def get_universally_compatible_meals(self) -> pd.DataFrame:
        """
        Get meals that are compatible with all people.
        
        Returns
        -------
        pd.DataFrame
            DataFrame of universally compatible meals
        """
        scores = self.score_meals()
        universal_meals = scores[scores == 1.0]
        
        return pd.DataFrame({
            'Meal': universal_meals.index,
            'Compatibility Score': universal_meals.values
        })
    
    def export_csv(self, path: str, use_emojis: bool = False):
        """
        Export the compatibility matrix to a CSV file.
        
        Parameters
        ----------
        path : str
            Path to save the CSV file
        use_emojis : bool, default=False
            Whether to use emoji checkmarks/crosses (✅/❌) instead of True/False
        """
        matrix = self.get_compatibility_matrix(use_emojis=use_emojis)
        matrix.to_csv(path, index=False)
    
    def export_markdown(self, path: str, use_emojis: bool = False):
        """
        Export the compatibility matrix to a Markdown file.
        
        Parameters
        ----------
        path : str
            Path to save the Markdown file
        use_emojis : bool, default=False
            Whether to use emoji checkmarks/crosses (✅/❌) instead of True/False
        """
        matrix = self.get_compatibility_matrix(use_emojis=use_emojis)
        with open(path, 'w') as f:
            f.write(matrix.to_markdown(index=False))

def analyze_meal_compatibility(meals: List[Meal], people: List[Person]) -> MealCompatibilityAnalyzer:
    """
    Create a MealCompatibilityAnalyzer from a list of meals and people.
    
    Parameters
    ----------
    meals : List[Meal]
        List of meals to analyze
    people : List[Person]
        List of people to check compatibility against
        
    Returns
    -------
    MealCompatibilityAnalyzer
        Analyzer object for the meal compatibility
    """
    return MealCompatibilityAnalyzer(meals, people) 