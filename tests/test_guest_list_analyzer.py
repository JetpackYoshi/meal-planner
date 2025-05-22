import pytest
import pandas as pd
from mealplanner.guest_list_analyzer import GuestListAnalyzer, analyze_guest_list
from mealplanner.dietary_model import Person, DietaryRestriction, tag_registry, FoodCategory
from mealplanner.defaults import setup_defaults

@pytest.fixture(autouse=True)
def setup_food_categories_and_tags():
    setup_defaults()
    yield
    FoodCategory.reset()
    tag_registry._tag_map.clear()

@pytest.fixture
def sample_guest_list():
    """Create a sample guest list for testing."""
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'Dietary Restriction': [
            'Vegan',
            'Vegetarian',
            'No nuts',
            'No shellfish',
            'No restrictions'
        ]
    }
    return pd.DataFrame(data)

def test_parse_guests(sample_guest_list):
    """Test that guests are correctly parsed into Person objects."""
    analyzer = GuestListAnalyzer(sample_guest_list)
    assert len(analyzer.people) == 5
    
    # Check that each person has the correct name and restriction
    names = {p.name for p in analyzer.people}
    assert names == {'Alice', 'Bob', 'Charlie', 'Diana', 'Eve'}
    
    # Check specific restrictions
    alice = next(p for p in analyzer.people if p.name == 'Alice')
    assert "ANIMAL_PRODUCTS" in alice.restriction.excluded
    
    bob = next(p for p in analyzer.people if p.name == 'Bob')
    assert {"MEAT", "FISH", "SHELLFISH"} == bob.restriction.excluded
    
    charlie = next(p for p in analyzer.people if p.name == 'Charlie')
    assert {"NUTS"} == charlie.restriction.excluded
    
    diana = next(p for p in analyzer.people if p.name == 'Diana')
    assert {"SHELLFISH"} == diana.restriction.excluded
    
    eve = next(p for p in analyzer.people if p.name == 'Eve')
    assert not eve.restriction.excluded

def test_get_implied_tags():
    """Test that implied tags are correctly generated."""
    analyzer = GuestListAnalyzer(pd.DataFrame({'Name': [], 'Dietary Restriction': []}))
    
    # Test vegan restrictions
    vegan_restriction = DietaryRestriction({"ANIMAL_PRODUCTS"})
    vegan_tags = analyzer._get_implied_tags(vegan_restriction)
    assert "DAIRY-FREE" in vegan_tags
    assert "EGG-FREE" in vegan_tags
    assert "MEAT-FREE" in vegan_tags
    assert "FISH-FREE" in vegan_tags
    assert "SHELLFISH-FREE" in vegan_tags
    
    # Test no restrictions
    no_restriction = DietaryRestriction(set())
    no_tags = analyzer._get_implied_tags(no_restriction)
    assert "NO-RESTRICTIONS" in no_tags

def test_get_restriction_summary(sample_guest_list):
    """Test that restriction summary is correctly generated."""
    analyzer = GuestListAnalyzer(sample_guest_list)
    summary = analyzer.get_restriction_summary()
    
    # Get the actual restriction strings from the analyzer
    alice = next(p for p in analyzer.people if p.name == 'Alice')
    bob = next(p for p in analyzer.people if p.name == 'Bob')
    charlie = next(p for p in analyzer.people if p.name == 'Charlie')
    diana = next(p for p in analyzer.people if p.name == 'Diana')
    
    assert summary["No restrictions"] == 1
    assert summary[str(alice.restriction)] == 1  # Vegan
    assert summary[str(bob.restriction)] == 1  # Vegetarian
    assert summary[str(charlie.restriction)] == 1  # No nuts
    assert summary[str(diana.restriction)] == 1  # No shellfish

def test_get_tag_summary(sample_guest_list):
    """Test that tag summary is correctly generated."""
    analyzer = GuestListAnalyzer(sample_guest_list)
    summary = analyzer.get_tag_summary()
    
    # Check basic tags
    assert summary["NO-RESTRICTIONS"] == 1
    assert summary["VEGAN"] == 1
    assert summary["VEGETARIAN"] == 2  # Updated: 2 people (vegan + vegetarian) imply VEGETARIAN
    assert summary["NUT-FREE"] == 1
    
    # Check implied tags through food category hierarchy
    assert summary["SHELLFISH-FREE"] == 3  # Vegan implies SHELLFISH-FREE through ANIMAL_PRODUCTS -> FISH -> SHELLFISH
    # Vegetarian implies SHELLFISH-FREE through FISH -> SHELLFISH
    # Diana explicitly has SHELLFISH-FREE

def test_get_restriction_matrix(sample_guest_list):
    """Test that restriction matrix is correctly generated."""
    analyzer = GuestListAnalyzer(sample_guest_list)
    matrix = analyzer.get_restriction_matrix()
    
    # Check matrix dimensions
    assert len(matrix) == 5  # 5 people
    assert "Name" in matrix.columns
    
    # Check specific restrictions
    alice_row = matrix[matrix["Name"] == "Alice"].iloc[0]
    assert not alice_row["ANIMAL_PRODUCTS"]  # Vegan can't eat animal products
    
    eve_row = matrix[matrix["Name"] == "Eve"].iloc[0]
    assert all(eve_row[col] for col in matrix.columns if col != "Name")  # No restrictions

def test_get_common_restrictions(sample_guest_list):
    """Test that common restrictions are correctly identified."""
    analyzer = GuestListAnalyzer(sample_guest_list)
    common = analyzer.get_common_restrictions(min_count=1)
    
    # Check individual restrictions
    assert common["ANIMAL_PRODUCTS"] == 1  # Alice (Vegan)
    assert common["MEAT"] == 1  # Bob (Vegetarian)
    assert common["NUTS"] == 1  # Charlie
    assert common["SHELLFISH"] == 2  # Bob (Vegetarian) and Diana
    assert common["FISH"] == 1  # Bob (Vegetarian)

def test_get_restriction_groups(sample_guest_list):
    """Test that restriction groups are correctly formed."""
    analyzer = GuestListAnalyzer(sample_guest_list)
    groups = analyzer.get_restriction_groups()
    
    # Get the actual restriction strings from the analyzer
    alice = next(p for p in analyzer.people if p.name == 'Alice')
    bob = next(p for p in analyzer.people if p.name == 'Bob')
    charlie = next(p for p in analyzer.people if p.name == 'Charlie')
    diana = next(p for p in analyzer.people if p.name == 'Diana')
    
    # Check that each person is in the correct group
    assert "Alice" in groups[str(alice.restriction)]
    assert "Bob" in groups[str(bob.restriction)]
    assert "Charlie" in groups[str(charlie.restriction)]
    assert "Diana" in groups[str(diana.restriction)]
    assert "Eve" in groups["No restrictions"]

def test_get_tag_groups(sample_guest_list):
    """Test that tag groups are correctly formed."""
    analyzer = GuestListAnalyzer(sample_guest_list)
    groups = analyzer.get_tag_groups()
    
    # Check that each person is in the correct tag groups
    assert "Alice" in groups["VEGAN"]
    assert "Bob" in groups["VEGETARIAN"]
    assert "Charlie" in groups["NUT-FREE"]
    assert "Diana" in groups["SHELLFISH-FREE"]
    assert "Eve" in groups["NO-RESTRICTIONS"]

def test_analyze_guest_list_function(sample_guest_list):
    """Test the analyze_guest_list convenience function."""
    analyzer = analyze_guest_list(sample_guest_list)
    assert isinstance(analyzer, GuestListAnalyzer)
    assert len(analyzer.people) == 5 