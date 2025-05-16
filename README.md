# Meal Planner

A flexible Python framework for modeling food categories, dietary restrictions, ingredients, meals, and analyzing meal compatibility for people with different dietary needs.

---

## Features

- **Hierarchical Food Categories:** Define and manage food categories with parent-child relationships (e.g., CHEESE → DAIRY → ANIMAL_PRODUCTS).
- **Dietary Restrictions:** Model dietary restrictions by excluding specific food categories (e.g., vegan, vegetarian, nut-free).
- **Ingredients & Meals:** Represent ingredients with metadata (category, calories, allergens) and group them into meals.
- **Compatibility Analysis:** Check if meals are compatible with individual or group dietary restrictions.
- **Tag System:** Register and generate canonical dietary tags (e.g., "VEGAN", "NUT-FREE").
- **Meal Compatibility Analyzer:** Analyze and visualize which meals are suitable for which people.
- **Export:** Export compatibility matrices as CSV or Markdown.

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/meal-planner.git
cd meal-planner
pip install -e .
```

---

## Usage

### 1. Define Food Categories

```python
from mealplanner.dietary_model import FoodCategory

FoodCategory.reset()
FoodCategory.define("ANIMAL_PRODUCTS")
FoodCategory.define("DAIRY", {"ANIMAL_PRODUCTS"})
FoodCategory.define("CHEESE", {"DAIRY"})
```

### 2. Register Dietary Tags

```python
from mealplanner.dietary_model import DietaryRestriction, tag_registry

tag_registry.register_tag("VEGAN", DietaryRestriction({"ANIMAL_PRODUCTS"}), category="ethical")
tag_registry.register_tag("NUT-FREE", DietaryRestriction({"NUTS"}), category="allergen")
```

### 3. Create Ingredients and Meals

```python
from mealplanner.dietary_model import Ingredient, Meal

cheese = Ingredient("Cheddar Cheese", FoodCategory.get("CHEESE"), 113, {"milk"})
meal = Meal("Cheese Sandwich", [cheese])
```

### 4. Define People and Restrictions

```python
from mealplanner.dietary_model import Person

person = Person("Alex", tag="VEGAN")
```

### 5. Analyze Meal Compatibility

```python
from mealplanner.dietary_model import MealCompatibilityAnalyzer

analyzer = MealCompatibilityAnalyzer([meal], [person])
analyzer.print_matrix(mode="markdown")
```

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

## Project Structure

```
meal-planner/
├── src/
│   └── mealplanner/
│       ├── __init__.py
│       └── dietary_model.py
├── tests/
│   └── test_dietary_model.py
├── docs/
│   └── index.rst
├── setup.py
└── README.md
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