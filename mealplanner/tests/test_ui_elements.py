import toga
# --- UI Element Tests ---

def test_main_window_title(app):
    app.startup()
    assert app.main_window.title == "Meal Planner"
    app.main_window.close()

def test_week_navigation_elements(app):
    app.startup()
    assert app.week_label is not None
    assert app.next_button is not None
    assert app.prev_button is not None
    app.main_window.close()

def test_day_labels_and_edit_buttons(app):
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

def test_set_weeks_button(app):
    app.startup()
    found_set_weeks_button = False
    for widget in app.main_window.content.children:
        if isinstance(widget, toga.Button) and widget.text == "Set Number of Weeks":
            found_set_weeks_button = True
            break
    assert found_set_weeks_button
    app.main_window.close()

# --- Week Navigation Tests ---

def test_next_week_button_click(app):
    app.startup()
    initial_week = app.current_week
    app.next_week(None)
    assert app.current_week == initial_week + 1
    app.main_window.close()

def test_prev_week_button_click(app):
    app.startup()
    app.current_week = 2
    initial_week = app.current_week
    app.prev_week(None)
    assert app.current_week == initial_week - 1
    app.main_window.close()

def test_week_label_updates(app):
    app.startup()
    app.current_week = 1
    initial_label_text = app.week_label.text
    app.next_week(None)
    app.update_week_display()
    assert app.week_label.text != initial_label_text
    app.main_window.close()


def test_set_number_of_weeks_invalid_input(tmp_path, app):
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

def test_edit_dinner_dialog(app, tmp_path):
    # Test the dialog that appears when "Edit" is pressed for a day.
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

def test_edit_dinner_cancel(app, tmp_path):
    app.DATA_FILE = str(tmp_path / "meal_plans.json")
    app.startup()
    app.weekly_plans = {1: {"Monday": "Original"}}
    app.edit_dinner(None, "Monday", 1)
    app.text_input.value = "New Meal"
    app.handle_edit_cancel(None)
    assert app.weekly_plans[1]["Monday"] == "Original"

def test_edit_then_save_and_reload(app, tmp_path):
    app.DATA_FILE = str(tmp_path / "meal_plans.json")
    app.startup()
    app.edit_dinner(None, "Monday", 1)
    app.text_input.value = "Pizza"
    app.handle_edit_ok(None)
    app.save_meals()

    new_app = app
    new_app.DATA_FILE = str(tmp_path / "meal_plans.json")
    new_app.weekly_plans = new_app.load_meals()
    assert new_app.weekly_plans[1]["Monday"] == "Pizza"
