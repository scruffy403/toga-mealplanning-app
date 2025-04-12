
# Meal Planner

A tool to plan ahead for meals.


## Test Coverage

Install the coverage tools

```bash
pip install pytest pytest-cov
```

Run this command to check test coverage

```bash
pytest --cov=src tests/
```

You should see an output similar to

```bash
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/mealplanner/__init__.py       0      0   100%
src/mealplanner/__main__.py       3      3     0%
src/mealplanner/app.py          252     19    92%
-------------------------------------------------
TOTAL                           255     22    91%
```
