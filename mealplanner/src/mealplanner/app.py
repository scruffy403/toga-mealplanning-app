import toga
from toga.style import Pack
from toga.style.pack import CENTER, RIGHT, END
from toga.constants import COLUMN, ROW
from functools import partial


class MealPlanner(toga.App):
    def startup(self):
        main_box = toga.Box(style=Pack(direction=ROW, margin=10))

        self.dinners = {
            "Monday": "Pasta",
            "Tuesday": "Tacos",
            "Wednesday": "Pizza",
            "Thursday": "Chicken and Veggies",
            "Friday": "Fish and Chips",
            "Saturday": "Steak",
            "Sunday": "Roast Dinner",
        }

        self.day_labels = {}

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            day_box = toga.Box(style=Pack(direction=COLUMN, justify_content=CENTER, margin=10))
            day_label = toga.Label(f"{day}:", style=Pack(text_align=CENTER))
            meal_label = toga.Label(self.dinners.get(day, "No dinner planned"), id=f"{day.lower()}-dinner", style=Pack(margin_bottom=10, text_align=CENTER))
            self.day_labels[day] = meal_label
            edit_button = toga.Button("Edit", on_press=partial(self.edit_dinner, day=day), style=Pack(width=100, text_align=CENTER))
            day_box.add(day_label)
            day_box.add(meal_label)
            day_box.add(edit_button)
            main_box.add(day_box)

        self.main_window = toga.MainWindow(title=self.formal_name, size=(800, 600))
        self.main_window.content = main_box
        self.main_window.show()

    def edit_dinner(self, widget, day):
        current_meal = self.dinners.get(day, "")
        text_input = toga.TextInput(value=current_meal)
        self.edit_window = toga.Window(title=f"Edit Dinner for {day}", resizable=True)

        content = toga.Box(style=Pack(direction=COLUMN, margin=10))
        content.add(toga.Label("Enter the new dinner:", style=Pack(margin_bottom=5)))
        content.add(text_input)

        def handle_ok(ok_button):
            new_meal = text_input.value
            self.edit_window.close()
            if new_meal is not None:
                self.dinners[day] = new_meal
                self.day_labels[day].text = new_meal

        def handle_cancel(cancel_button):
            self.edit_window.close()

        ok_button = toga.Button("OK", on_press=handle_ok, style=Pack(width=60, margin=5))
        cancel_button = toga.Button("Cancel", on_press=handle_cancel, style=Pack(width=60, margin=5))

        button_box = toga.Box(style=Pack(direction=ROW, margin=20))
        button_box.add(ok_button)
        button_box.add(cancel_button)

        content.add(button_box)
        self.edit_window.content = content
        self.edit_window.show()


def main():
    return MealPlanner()
