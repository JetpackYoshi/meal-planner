# Meal Planner

A flexible Python framework for modeling food categories, dietary restrictions, ingredients, meals, and analyzing meal compatibility for people with different dietary needs.

---

## Features

- **Flexible Food Category Hierarchy:**  
  Define custom food categories with parent-child relationships (e.g., CHEESE → DAIRY → ANIMAL_PRODUCTS). Supports dynamic nesting and inheritance for powerful dietary modeling.

- **Dietary Restriction Modeling:**  
  Represent dietary needs by excluding specific food categories (e.g., vegan, vegetarian, pescatarian, allergen-free). Easily check if foods or meals are allowed under a restriction.

- **Ingredient Representation:**  
  Store ingredient details including name, food category, calories, and allergens.

- **Meal Construction:**  
  Group ingredients into meals. Meals can be analyzed for compatibility with dietary restrictions.

- **Dietary Tag System:**  
  Register and manage canonical dietary tags (e.g., "VEGAN", "NUT-FREE", "DAIRY-FREE") with category support (e.g., "ethical", "allergen"). Generate tags for custom restrictions.

- **Person Profiles:**  
  Assign dietary tags or custom restrictions to people for compatibility checks. Supports both tag-based and custom restriction-based profiles.

- **Meal Compatibility Analysis:**  
  - Determine which meals meet the dietary needs of individuals or groups.
  - Build and visualize compatibility matrices.
  - Score meals by number of compatible people.
  - Find universally compatible meals.
  - Export compatibility matrices in CSV or Markdown formats.

- **Natural Language Parsing:**  
  Parse freeform dietary restriction descriptions (e.g., "vegetarian and dairy free", "no nuts") into structured restrictions using keyword and fuzzy matching.

- **Extensible API:**  
  Easily extend categories, tags, and analysis logic for custom use cases.

- **Interactive Examples:**  
  Explore features and workflows in the [`examples/feature_overview.ipynb`](examples/feature_overview.ipynb) Jupyter notebook, including visualization of compatibility results.

- **Comprehensive Testing:**  
  Includes a suite of unit tests for core functionality.

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/JetpackYoshi/meal-planner.git
cd meal-planner
pip install -e .
```

---

## Usage

### 1. Define Food Categories

Define a hierarchy of food categories for flexible dietary modeling.

```python
from mealplanner.dietary_model import FoodCategory

FoodCategory.reset()
FoodCategory.define("ANIMAL_PRODUCTS")
FoodCategory.define("MEAT", {"ANIMAL_PRODUCTS"})
FoodCategory.define("DAIRY", {"ANIMAL_PRODUCTS"})
FoodCategory.define("CHEESE", {"DAIRY"})
FoodCategory.define("NUTS")
```

### 2. Register Dietary Tags

Register canonical dietary tags for common restrictions.

```python
from mealplanner.dietary_model import DietaryRestriction, tag_registry

tag_registry.register_tag("VEGAN", DietaryRestriction({"ANIMAL_PRODUCTS"}), category="ethical")
tag_registry.register_tag("NUT-FREE", DietaryRestriction({"NUTS"}), category="allergen")
```

### 3. Create Ingredients and Meals

Create ingredients with metadata and group them into meals.

```python
from mealplanner.dietary_model import Ingredient, Meal

cheese = Ingredient("Cheddar Cheese", FoodCategory.get("CHEESE"), 113, {"milk"})
almond = Ingredient("Almond", FoodCategory.get("NUTS"), 150, {"almond"})
meal = Meal("Cheese & Almond Plate", [cheese, almond])
```

### 4. Define People and Restrictions

Assign dietary tags or custom restrictions to people.

```python
from mealplanner.dietary_model import Person, DietaryRestriction

person1 = Person("Alex", tag="VEGAN")
person2 = Person("Sam", restriction=DietaryRestriction({"NUTS"}))
```

### 5. Analyze Meal Compatibility

Analyze which meals are compatible with which people.

```python
from mealplanner.dietary_model import MealCompatibilityAnalyzer

meals = [meal]
people = [person1, person2]
analyzer = MealCompatibilityAnalyzer(meals, people)
analyzer.print_matrix(mode="markdown")
```

### 6. Parse Natural Language Restrictions

Convert freeform dietary descriptions into structured restrictions.

```python
from mealplanner.natural_language_parsing import parse_freeform_restriction

restriction = parse_freeform_restriction("vegetarian and dairy free")
```

### 7. Explore Interactive Examples

See [`examples/feature_overview.ipynb`](examples/feature_overview.ipynb) for a full workflow, including visualization and advanced features.

---

## Documentation

- **API Reference:** See the [docs/index.rst](docs/index.rst) or build the Sphinx documentation:
  ```bash
  cd docs
  make html
  ```
  Open `_build/html/index.html` in your browser.

---

## Running Tests

Tests are located in the `tests/` directory and use `pytest`:

```bash
pytest
```

---

## Contributing

1. Fork the repository.
2. Create a new branch.
3. Make your changes and add tests.
4. Submit a pull request.

---

## License

MIT License

---

## Acknowledgments

- Inspired by real-world dietary planning needs.
- Uses [pandas](https://pandas.pydata.org/) for compatibility matrix analysis.