import json

def test_load_settings_from_file(app, tmp_path):
    # Create a temporary data file with a specific num_weeks
    settings_data = {"num_weeks": 6}
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        json.dump(settings_data, f)

    # Use the app fixture, which already initializes the app
    app.DATA_FILE = str(test_file)  # Set the file path to the temporary file
    app.load_settings()  # Load settings from the file

    assert app.num_weeks == 6

def test_load_settings_default_no_file(app):
    app.DATA_FILE = "non_existent_file.json"
    app.load_settings()
    assert app.num_weeks == 4

def test_get_default_weekly_meals_structure(app):
    meals = app.get_default_weekly_meals()
    assert isinstance(meals, dict)
    assert 1 in meals
    assert "Monday" in meals[1]

def test_load_meals_missing_file(app,tmp_path):
    app.DATA_FILE = str(tmp_path / "non_existent.json")
    default_meals = app.get_default_weekly_meals()
    loaded_meals = app.load_meals()
    assert loaded_meals == default_meals
