from src.mealplanner.app import MealPlanner
from datetime import date, timedelta
import json

def test_save_meals(app,tmp_path):
    # Create a temporary data file
    test_file = tmp_path / "meal_plans.json"
    app.DATA_FILE = str(test_file)
    # Ensure the file exists before writing to it
    test_file.touch()

    # Prepare some meal data
    app.num_weeks = 2
    app.plan_start_date = date(2024, 2, 19)
    app.weekly_plans = {
        1: {
            "Monday": "Chicken",
            "Tuesday": "Beef",
        },
        2: {
            "Wednesday": "Pasta",
            "Thursday": "Fish",
        },
    }

    # Call the save_meals method
    app.save_meals()

    # Load the data from the file
    try:
        with open(str(test_file), "r") as f:
            saved_data = json.load(f)
    except json.JSONDecodeError:
        saved_data = {}

    # Assert the saved data matches the prepared data
    expected_data = {
        "weeks": {
            "1": {
                "Monday": "Chicken",
                "Tuesday": "Beef",
            },
            "2": {
                "Wednesday": "Pasta",
                "Thursday": "Fish",
            },
        },
        "start_date": "2024-02-19",
        "num_weeks": 2,
    }
    assert saved_data == expected_data
