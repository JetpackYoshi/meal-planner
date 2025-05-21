import pandas as pd
from mealplanner.guest_list_analyzer import analyze_guest_list
from mealplanner.dietary_model import tag_registry, DietaryRestriction

# Initialize tag registry with common dietary tags
tag_registry.register_tag("VEGAN", DietaryRestriction({"ANIMAL_PRODUCTS"}), category="ethical")
tag_registry.register_tag("VEGETARIAN", DietaryRestriction({"MEAT", "FISH", "SHELLFISH"}), category="ethical")
tag_registry.register_tag("PESCATARIAN", DietaryRestriction({"MEAT"}), category="ethical")
tag_registry.register_tag("NUT-FREE", DietaryRestriction({"NUTS"}), category="allergen")
tag_registry.register_tag("DAIRY-FREE", DietaryRestriction({"DAIRY"}), category="allergen")
tag_registry.register_tag("EGG-FREE", DietaryRestriction({"EGGS"}), category="allergen")
tag_registry.register_tag("SHELLFISH-FREE", DietaryRestriction({"SHELLFISH"}), category="allergen")
tag_registry.register_tag("FISH-FREE", DietaryRestriction({"FISH"}), category="allergen")
tag_registry.register_tag("MEAT-FREE", DietaryRestriction({"MEAT"}), category="ethical")
tag_registry.register_tag("BEEF-FREE", DietaryRestriction({"BEEF"}), category="allergen")

# Example guest list data
guest_data = {
    'Name': [
        'Omny Miranda Martone',
        'Kelly Williams',
        'Marisa Edmondson',
        'Raktima',
        'Alexis Bryant',
        'Berkley Delmonico',
        'Delia Parrish',
        'Julia Bodily',
        'Justine Frank',
        'Kelsey Hartman',
        'Sydney Moss',
        'Sally Watanabe',
        'Uyen-Truc Nguyen',
        'Jessie Cali',
        'Abbi Olivieri',
        'Alexis Abraham',
        'hongbin zhang',
        'Yoshika Govender',
        'Sara Anderson',
        'Liz Nagel',
        'Kinsey Alexander',
        'Cadia Montero',
        'Mo Wilkie',
        'Rachel Newstadt',
        'Ruby Dennis',
        'Charlotte delavaloire',
        'Brittany Sincox',
        'Anita Pan'
    ],
    'Dietary Restriction': [
        'Vegan (no meat, milk, egg)',
        'Nope!',
        'Nuts (except almonds) shellfish',
        'No beef',
        'No',
        'No',
        'Lactose intolerant',
        'No',
        'vegan',
        'Vegetarian',
        'Vegetarian',
        'nawww',
        'No',
        'No',
        'Vegetarian and Dairy free',
        'No',
        'nope',
        'Nope!',
        'Veggie',
        'No',
        'Vegetarian',
        'No',
        'No',
        'vegetarian',
        'No',
        'Vegetarian',
        'No',
        'None!'
    ]
}

def main():
    # Create DataFrame from guest data
    guest_list = pd.DataFrame(guest_data)
    
    # Create analyzer
    analyzer = analyze_guest_list(guest_list)
    
    # Get and print restriction summary
    print("\n=== Dietary Restriction Summary ===")
    summary = analyzer.get_restriction_summary()
    for restriction, count in sorted(summary.items(), key=lambda x: (-x[1], x[0])):
        print(f"{restriction}: {count} people")
    
    # Get and print tag summary
    print("\n=== Canonical Tag Summary ===")
    tag_summary = analyzer.get_tag_summary()
    for tag, count in sorted(tag_summary.items(), key=lambda x: (-x[1], x[0])):
        print(f"{tag}: {count} people")
    
    # Get and print common restrictions
    print("\n=== Common Restrictions (2+ people) ===")
    common = analyzer.get_common_restrictions(min_count=2)
    for category, count in sorted(common.items(), key=lambda x: (-x[1], x[0])):
        print(f"{category}: {count} people")
    
    # Get and print restriction groups
    print("\n=== People by Restriction Group ===")
    groups = analyzer.get_restriction_groups()
    for restriction, names in sorted(groups.items()):
        print(f"\n{restriction}:")
        for name in sorted(names):
            print(f"  - {name}")
    
    # Get and print tag groups
    print("\n=== People by Canonical Tag ===")
    tag_groups = analyzer.get_tag_groups()
    for tag, names in sorted(tag_groups.items()):
        print(f"\n{tag}:")
        for name in sorted(names):
            print(f"  - {name}")
    
    print("\n=== Restriction Matrix (✅/❌) ===")
    matrix = analyzer.get_restriction_matrix(use_emojis=True)
    print(matrix.to_string(index=False))

if __name__ == "__main__":
    main() 