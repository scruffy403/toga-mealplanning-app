from src.mealplanner.app import MealPlanner
import json
from datetime import date, timedelta
import toga

def test_initial_state():
    app = MealPlanner()
    assert app.weekly_plans == {}
    assert app.current_week == 1
    assert app.day_labels == {}
    assert app.plan_start_date is None
    assert app.num_weeks == 4


# Tests for load_start_date
def test_load_start_date_from_file(app,tmp_path):
    # Create a temporary data file with a specific start_date
    start_date = date(2025, 1, 27)  # Example start date (Monday)
    settings_data = {"start_date": start_date.strftime('%Y-%m-%d')}
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        json.dump(settings_data, f)
    app.DATA_FILE = str(test_file)
    loaded_start_date = app.load_start_date()
    assert loaded_start_date == start_date

def test_load_start_date_missing_from_file(app,tmp_path):
    # Create a temporary data file without start_date
    settings_data = {}
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        json.dump(settings_data, f)

    app.DATA_FILE = str(test_file)
    loaded_start_date = app.load_start_date()
    # Default start date is Monday of the current week.
    expected_start_date = date.today() + timedelta(days=-date.today().weekday())
    assert loaded_start_date == expected_start_date

def test_load_start_date_invalid_format(app,tmp_path):
    # Create a temporary data file with an invalid date format
    settings_data = {"start_date": "invalid-date-format"}
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        json.dump(settings_data, f)

    app.DATA_FILE = str(test_file)
    loaded_start_date = app.load_start_date()
    expected_start_date = date.today() + timedelta(days=-date.today().weekday())
    assert loaded_start_date == expected_start_date


# --- Week Navigation Tests ---
def test_load_settings_invalid_json(app, tmp_path):
    # Create a temporary data file with invalid JSON
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        f.write("This is not valid JSON")
    app = MealPlanner()
    app.DATA_FILE = str(test_file)
    app.load_settings()
    assert app.num_weeks == 4


def test_load_meals_empty_file(app, tmp_path):
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        f.write("")  # Create an empty file
    app.DATA_FILE = str(test_file)
    default_meals = app.get_default_weekly_meals()
    loaded_meals = app.load_meals()
    assert loaded_meals == default_meals

def create_app():
    """Create a new MealPlanner application for each test."""
    return MealPlanner()

def create_main_window(app):
    """Start the application and return the main window."""
    app.startup()
    main_window = app.main_window
    return main_window



def test_clear_messages_interaction(app):
    """Test clearing messages through the UI."""
    app.startup()
    main_window = app.main_window
    # Add some messages
    app.stdout_label.text = "Message 1"
    app.stderr_label.text = "Error 1"

    # Find the "Clear Messages" button
    clear_button = None
    for widget in main_window.content.children:
        if isinstance(widget, toga.Button) and widget.text == "Clear Messages":
            clear_button = widget
            break
    assert clear_button is not None

    # Click the button
    clear_button.on_press()  # Simulate Click

    # Check that the labels are empty
    assert app.stdout_label.text == ""
    assert app.stderr_label.text == ""
    app.main_window.close()



def test_navigation_button_state(app):
    app.startup()
    app.current_week = 1
    app.update_navigation_buttons()
    assert not app.prev_button.enabled
    assert app.next_button.enabled
    app.current_week = app.num_weeks
    app.update_navigation_buttons()
    assert app.prev_button.enabled
    assert not app.next_button.enabled
    app.main_window.close()


def test_set_number_of_weeks_dialog(app, tmp_path):
    # Test the dialog that appears when "Set Number of Weeks" is pressed.
    app.DATA_FILE = str(tmp_path / "meal_plans.json") # Use a temp file
    app.startup()

    # Simulate showing the dialog
    app.show_set_weeks_dialog(None)  # Pass None as widget, as it's not used.
    assert app.set_weeks_window is not None
    assert app.weeks_input_widget is not None

    # Simulate entering a value and pressing OK
    app.weeks_input_widget.value = "8"
    app.handle_set_weeks_ok(None) # Pass None

    # Check that num_weeks was updated
    assert app.num_weeks == 8
