from src.mealplanner.app import MealPlanner
import pytest


@pytest.fixture
def app():
    return MealPlanner()
