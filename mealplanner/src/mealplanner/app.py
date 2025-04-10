import toga
from toga.style import Pack
from toga.style.pack import CENTER, RIGHT, END, LEFT, BOLD
from toga.constants import COLUMN, ROW
from functools import partial
import json
import os
import datetime
import sys  # Import the sys module
import datetime

DATA_FILE = "meal_plans.json"
# NUM_WEEKS will now be loaded/set dynamically

class MealPlanner(toga.App):
    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, margin=10))  # Changed to COLUMN

        self.load_settings() # Load NUM_WEEKS and potentially other settings
        self.weekly_plans = self.load_meals()
        self.current_week = 1  # Start with the first week
        self.day_labels = {}
        self.plan_start_date = self.load_start_date() # Load or default start date

        # Week navigation buttons
        week_nav_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=10))
        prev_button = toga.Button("< Previous Week", on_press=self.prev_week, style=Pack(flex=1))
        next_button = toga.Button("Next Week >", on_press=self.next_week, style=Pack(flex=1))
        self.week_label = toga.Label(f"Week {self.current_week}: {self.get_week_display_date()}", style=Pack(width=250, text_align=CENTER)) # Dynamic date display
        self.next_button = next_button # Store a reference

        week_nav_box.add(prev_button)
        week_nav_box.add(self.week_label)
        week_nav_box.add(next_button)
        main_box.add(week_nav_box)

        # Set Number of Weeks Button
        set_weeks_button = toga.Button("Set Number of Weeks", on_press=self.show_set_weeks_dialog, style=Pack(margin_bottom=10))
        main_box.add(set_weeks_button)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            day_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=10)) # Changed to ROW
            day_label = toga.Label(f"{day}:", style=Pack(width=100, text_align=RIGHT))
            meal_label = toga.Label(self.weekly_plans.get(self.current_week, {}).get(day, "No dinner planned"), id=f"{day.lower()}-dinner", style=Pack(width=200, text_align=LEFT)) # Adjusted width and
            self.day_labels[day] = meal_label
            edit_button = toga.Button("Edit", on_press=partial(self.edit_dinner, day=day, week=self.current_week), style=Pack(width=80)) # Passing current_week
            day_box.add(day_label)
            day_box.add(meal_label)
            day_box.add(edit_button)
            main_box.add(day_box)

        # Message Area with Title and ScrollContainer
        message_title = toga.Label("Messages:", style=Pack(margin_top=15, font_weight='bold'))
        clear_button = toga.Button("Clear Messages", on_press=self.clear_messages, style=Pack(margin_top=8))
        self.stdout_label = toga.Label("", style=Pack(text_align=LEFT, color='darkgreen', margin=5, font_size=10))
        self.stderr_label = toga.Label("", style=Pack(text_align=LEFT, color='red', margin=5, font_size=10))

        message_content_box = toga.Box(style=Pack(direction=COLUMN)) # Box to hold both labels
        message_content_box.add(self.stdout_label)
        message_content_box.add(self.stderr_label)

        message_scroll = toga.ScrollContainer(content=message_content_box, style=Pack(flex=1, height=100))

        main_box.add(message_title)
        main_box.add(message_scroll)
        main_box.add(clear_button)

        self.main_window = toga.MainWindow(title=self.formal_name, size=(800, 600))
        self.main_window.content = main_box
        self.main_window.show()
        self.update_week_display()
        self.update_navigation_buttons()

        # Redirect stdout and stderr to our separate labels
        sys.stdout = self.GUIConsole(self.stdout_label)
        self.stderr_console = self.GUIConsole(self.stderr_label, is_stderr=True)
        sys.stderr = self.GUIConsole(self.stderr_label)

    class GUIConsole:
        def __init__(self, text_widget, is_stderr=False):
            self.text_widget = text_widget
            self.is_stderr = is_stderr

        def write(self, message):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prefix = "Info: " if not self.is_stderr else "Error: "
            formatted_message = f"{timestamp} - {prefix}{message}\n"
            self.text_widget.text = self.text_widget.text + formatted_message

        def flush(self):
            pass

    def clear_messages(self, widget):
            self.stdout_label.text = ""
            self.stderr_label.text = ""

    def load_settings(self):
        global NUM_WEEKS
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    NUM_WEEKS = data.get('num_weeks', 4) # Default to 4 if not found
            except (json.JSONDecodeError, FileNotFoundError):
                NUM_WEEKS = 4
        else:
            NUM_WEEKS = 4

    def load_meals(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    weekly_data_str_keys = data.get('weeks', {})
                    weekly_data = {}
                    for week_str, meals in weekly_data_str_keys.items():
                        try:
                            week_int = int(week_str)
                            weekly_data[week_int] = meals
                        except ValueError:
                            sys.stderr.write(f"Warning: Skipping invalid week key in data file: {week_str}")

                    # Ensure we have enough weeks in the data (using integer keys now)
                    for week in range(1, NUM_WEEKS + 1):
                        if week not in weekly_data:
                            weekly_data[week] = self.get_default_week_meals()

                    start_date_str = data.get('start_date')
                    if start_date_str:
                        self.plan_start_date = self.parse_date(start_date_str)
                    else:
                        self.plan_start_date = self.get_default_start_date()
                    return weekly_data
            except (json.JSONDecodeError, FileNotFoundError):
                sys.stderr.write(f"Error loading or file not found: {DATA_FILE}. Using default.")
                return self.get_default_weekly_meals()
        else:
            return self.get_default_weekly_meals()

    def parse_date(self, date_str):
        try:
            return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return self.get_default_start_date()

    def get_default_start_date(self):
        return datetime.date.today() + datetime.timedelta(days=-datetime.date.today().weekday()) # Default to current week's Monday

    def load_start_date(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    start_date_str = data.get('start_date')
                    if start_date_str:
                        return self.parse_date(start_date_str)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return self.get_default_start_date()

    def get_default_weekly_meals(self):
        default_meals = self.get_default_week_meals()
        return {week: default_meals.copy() for week in range(1, NUM_WEEKS + 1)}

    def get_default_week_meals(self):
        return {
            "Monday": "Pasta",
            "Tuesday": "Tacos",
            "Wednesday": "Pizza",
            "Thursday": "Chicken and Veggies",
            "Friday": "Fish and Chips",
            "Saturday": "Steak",
            "Sunday": "Roast Dinner",
        }

    def save_meals(self):
        sys.stdout.write("save_meals() called")
        data_to_save = {'weeks': self.weekly_plans, 'start_date': self.plan_start_date.strftime('%Y-%m-%d') if self.plan_start_date else None, 'num_weeks': NUM_WEEKS}
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(data_to_save, f, indent=4)
        except IOError:
            sys.stderr.write(f"Error saving: {f}")
            sys.stderr.write(f"Error saving meals to {DATA_FILE}.")

    def prev_week(self, widget):
        if self.current_week > 1:
            self.current_week -= 1
            self.update_week_display()
            self.update_edit_button_callbacks()
            self.update_navigation_buttons()

    def next_week(self, widget):
        if self.current_week < NUM_WEEKS:
            self.current_week += 1
            self.update_week_display()
            self.update_edit_button_callbacks()
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        self.next_button.enabled = self.current_week < NUM_WEEKS

    def update_edit_button_callbacks(self):
        for widget in self.main_window.content.children[2:]: # Skip week nav and set weeks button
            if isinstance(widget, toga.Box): # Each day is in a Box
                for sub_widget in widget.children:
                    if isinstance(sub_widget, toga.Button) and sub_widget.text == "Edit":
                        day = widget.children[0].text[:-1] # Extract the day from the label
                        sub_widget.on_press = partial(self.edit_dinner, day=day, week=self.current_week)

    def get_week_display_date(self):
        if self.plan_start_date:
            start_date = self.plan_start_date + datetime.timedelta(days=(self.current_week - 1) * 7)
            return start_date.strftime('%Y-%m-%d')
        else:
            return 'Not Set'

    def update_week_display(self):
        self.week_label.text = f"Week {self.current_week}: {self.get_week_display_date()}"
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            meal = self.weekly_plans.get(self.current_week, {}).get(day, "No dinner planned")
            self.day_labels[day].text = meal

    def show_set_weeks_dialog(self, widget):
        self.set_weeks_window = toga.Window(title="Set Number of Weeks", resizable=False)
        weeks_input = toga.TextInput(style=Pack(margin=10))
        self.weeks_input_widget = weeks_input # Store a reference
        ok_button = toga.Button("OK", on_press=self.handle_set_weeks_ok, style=Pack(margin=10))
        cancel_button = toga.Button("Cancel", on_press=lambda btn: self.set_weeks_window.close(), style=Pack(margin=10))

        button_box = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin=10))
        button_box.add(ok_button)
        button_box.add(cancel_button)

        content_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        content_box.add(toga.Label("Enter the desired number of weeks:", style=Pack(margin_bottom=5)))
        content_box.add(weeks_input)
        content_box.add(button_box)

        self.set_weeks_window.content = content_box
        self.set_weeks_window.show()

    def shutdown(self):
        self.save_meals()

    def edit_dinner(self, widget, day, week):
        current_meal = self.weekly_plans.get(week, {}).get(day, "")
        text_input = toga.TextInput(value=current_meal)
        self.edit_window = toga.Window(title=f"Edit Dinner for Week {week}, {day}", resizable=True)

        content = toga.Box(style=Pack(direction=COLUMN, margin=10))
        content.add(toga.Label("Enter the new dinner:", style=Pack(margin_bottom=5)))
        content.add(text_input)

        def handle_ok(ok_button):
            sys.stderr.write("This message should be red.\n")
            new_meal = text_input.value
            self.edit_window.close()
            if new_meal is not None:
                self.weekly_plans[week][day] = new_meal
                self.update_week_display() # Force a re-render of the current week's labels
                self.save_meals()

        def handle_cancel(cancel_button):
            self.edit_window.close()

        ok_button = toga.Button("OK", on_press=handle_ok, style=Pack(width=60, margin=5))
        cancel_button = toga.Button("Cancel", on_press=handle_cancel, style=Pack(width=60, margin=5))

        button_box = toga.Box(style=Pack(direction=ROW, justify_content=END, margin_top=20))
        button_box.add(ok_button)
        button_box.add(cancel_button)

        content.add(button_box)
        self.edit_window.content = content
        self.edit_window.show()

def main():
    return MealPlanner()
