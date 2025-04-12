from src.mealplanner.app import MealPlanner
import os
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

def test_load_settings_from_file(tmp_path):
    # Create a temporary data file with a specific num_weeks
    settings_data = {"num_weeks": 6}
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        json.dump(settings_data, f)

    app = MealPlanner()
    app.DATA_FILE = str(test_file)
    app.load_settings()
    assert app.num_weeks == 6

def test_load_settings_default_no_file():
    app = MealPlanner()
    app.DATA_FILE = "non_existent_file.json"
    app.load_settings()
    assert app.num_weeks == 4

def test_get_default_weekly_meals_structure():
    app = MealPlanner()
    meals = app.get_default_weekly_meals()
    assert isinstance(meals, dict)
    assert 1 in meals
    assert "Monday" in meals[1]

def test_load_meals_missing_file(tmp_path):
    app = MealPlanner()
    app.DATA_FILE = str(tmp_path / "non_existent.json")
    default_meals = app.get_default_weekly_meals()
    loaded_meals = app.load_meals()
    assert loaded_meals == default_meals

# Tests for load_start_date
def test_load_start_date_from_file(tmp_path):
    # Create a temporary data file with a specific start_date
    start_date = date(2025, 1, 27)  # Example start date (Monday)
    settings_data = {"start_date": start_date.strftime('%Y-%m-%d')}
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        json.dump(settings_data, f)

    app = MealPlanner()
    app.DATA_FILE = str(test_file)
    loaded_start_date = app.load_start_date()
    assert loaded_start_date == start_date

def test_load_start_date_missing_from_file(tmp_path):
    # Create a temporary data file without start_date
    settings_data = {}
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        json.dump(settings_data, f)

    app = MealPlanner()
    app.DATA_FILE = str(test_file)
    loaded_start_date = app.load_start_date()
    # Default start date is Monday of the current week.
    expected_start_date = date.today() + timedelta(days=-date.today().weekday())
    assert loaded_start_date == expected_start_date

def test_load_start_date_invalid_format(tmp_path):
    # Create a temporary data file with an invalid date format
    settings_data = {"start_date": "invalid-date-format"}
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        json.dump(settings_data, f)

    app = MealPlanner()
    app.DATA_FILE = str(test_file)
    loaded_start_date = app.load_start_date()
    expected_start_date = date.today() + timedelta(days=-date.today().weekday())
    assert loaded_start_date == expected_start_date

def test_save_meals(tmp_path):
    # Create a temporary data file
    test_file = tmp_path / "meal_plans.json"
    app = MealPlanner()
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


# --- UI Element Tests ---

def test_main_window_title():
    app = MealPlanner()
    app.startup()
    assert app.main_window.title == "Meal Planner"
    app.main_window.close()

def test_week_navigation_elements():
    app = MealPlanner()
    app.startup()
    assert app.week_label is not None
    assert app.next_button is not None
    assert app.prev_button is not None
    app.main_window.close()

def test_day_labels_and_edit_buttons():
    app = MealPlanner()
    app.startup()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        assert day in app.day_labels
        # Check for the existence of the edit button.
        found_edit_button = False
        for widget in app.main_window.content.children:
            if isinstance(widget, toga.Box):
                for sub_widget in widget.children:
                    if isinstance(sub_widget, toga.Button) and sub_widget.text == "Edit":
                        found_edit_button = True
                        break
        assert found_edit_button
    app.main_window.close()

def test_message_area_and_clear_button():
    app = MealPlanner()
    app.startup()
    assert app.stdout_label is not None
    assert app.stderr_label is not None
    # Check for the existence of the clear button.
    found_clear_button = False
    for widget in app.main_window.content.children:
        if isinstance(widget, toga.Button) and widget.text == "Clear Messages":
            found_clear_button = True
            break
    assert found_clear_button
    app.main_window.close()

def test_set_weeks_button():
    app = MealPlanner()
    app.startup()
    found_set_weeks_button = False
    for widget in app.main_window.content.children:
        if isinstance(widget, toga.Button) and widget.text == "Set Number of Weeks":
            found_set_weeks_button = True
            break
    assert found_set_weeks_button
    app.main_window.close()

# --- Week Navigation Tests ---

def test_next_week_button_click():
    app = MealPlanner()
    app.startup()
    initial_week = app.current_week
    app.next_week(None)
    assert app.current_week == initial_week + 1
    app.main_window.close()

def test_prev_week_button_click():
    app = MealPlanner()
    app.startup()
    app.current_week = 2
    initial_week = app.current_week
    app.prev_week(None)
    assert app.current_week == initial_week - 1
    app.main_window.close()

def test_week_label_updates():
    app = MealPlanner()
    app.startup()
    app.current_week = 1
    initial_label_text = app.week_label.text
    app.next_week(None)
    app.update_week_display()
    assert app.week_label.text != initial_label_text
    app.main_window.close()


def test_set_number_of_weeks_invalid_input(tmp_path):
    # Test with invalid input (non-integer) in the "Set Number of Weeks" dialog.
    app = MealPlanner()
    app.DATA_FILE = str(tmp_path / "meal_plans.json")
    app.startup()

    app.show_set_weeks_dialog(None)
    app.weeks_input_widget.value = "abc"
    app.handle_set_weeks_ok(None)

    # Check that num_weeks remains at the default value
    assert app.num_weeks == 4
    # Check that the error message is displayed
    assert "Invalid Input!" in app.stderr_label.text
    app.main_window.close()

def test_edit_dinner_dialog(tmp_path):
    # Test the dialog that appears when "Edit" is pressed for a day.
    app = MealPlanner()
    app.DATA_FILE = str(tmp_path / "meal_plans.json")
    app.startup()
    day = "Monday"
    week = 1

    # Simulate showing the dialog
    app.edit_dinner(None, day, week)

    # Check the initial state of the dialog
    assert app.edit_window is not None
    assert app.text_input is not None  # Changed to use the stored text_input

    # Simulate entering a new meal and pressing OK
    new_meal = "New Meal"
    app.text_input.value = new_meal
    app.handle_edit_ok(None)  # Added None

    # Check that the meal was updated
    assert app.weekly_plans[week][day] == new_meal

def test_edit_dinner_cancel(tmp_path):
    app = MealPlanner()
    app.DATA_FILE = str(tmp_path / "meal_plans.json")
    app.startup()
    app.weekly_plans = {1: {"Monday": "Original"}}
    app.edit_dinner(None, "Monday", 1)
    app.text_input.value = "New Meal"
    app.handle_edit_cancel(None)
    assert app.weekly_plans[1]["Monday"] == "Original"

def test_edit_then_save_and_reload(tmp_path):
    app = MealPlanner()
    app.DATA_FILE = str(tmp_path / "meal_plans.json")
    app.startup()
    app.edit_dinner(None, "Monday", 1)
    app.text_input.value = "Pizza"
    app.handle_edit_ok(None)
    app.save_meals()

    new_app = MealPlanner()
    new_app.DATA_FILE = str(tmp_path / "meal_plans.json")
    new_app.weekly_plans = new_app.load_meals()
    assert new_app.weekly_plans[1]["Monday"] == "Pizza"

def test_load_settings_invalid_json(tmp_path):
    # Create a temporary data file with invalid JSON
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        f.write("This is not valid JSON")
    app = MealPlanner()
    app.DATA_FILE = str(test_file)
    app.load_settings()
    assert app.num_weeks == 4


def test_load_meals_empty_file(tmp_path):
    test_file = tmp_path / "meal_plans.json"
    with open(test_file, "w") as f:
        f.write("")  # Create an empty file
    app = MealPlanner()
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



def test_clear_messages_interaction():
    """Test clearing messages through the UI."""
    app = MealPlanner()
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



def test_navigation_button_state():
    app = MealPlanner()
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


def test_set_number_of_weeks_dialog(tmp_path):
    # Test the dialog that appears when "Set Number of Weeks" is pressed.
    app = MealPlanner()
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
