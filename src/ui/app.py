# app.py
from __future__ import annotations

import sys
from typing import Iterable
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
from styles import APP_STYLE

from pages.home_page import HomePage
from pages.new_meal_page import NewMealPage
from pages.favorites_page import FavoritesPage
from pages.history_page import HistoryPage, HistoryDay
from pages.new_ingredient_page import NewIngredientPage

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meals")

        # --- Stack & layout ---------------------------------------------------
        self.stack = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

        # --- Pages ------------------------------------------------------------
        self._build_pages()

    # -------------------------------------------------------------------------
    # Page factory / wiring
    # -------------------------------------------------------------------------
    def _build_pages(self) -> None:
        # Home
        self.home = HomePage(
            goto_new_meal=self.go_new_meal,
            goto_favorites=self.go_favorites,
            goto_history=self.go_history,
            goto_new_ingredient=self.go_new_ingredient
        )

        # New Meal
        self.new_meal = NewMealPage(
            go_back=self.go_home,
            on_create=self.on_create_meal
        )

        # Favorites
        self.favorites = FavoritesPage(
            go_back=self.go_home,
            on_use_meal=self.use_favorite_in_new_meal,
            on_delete_meal=self.delete_favorite,
            initial_meals=["Meal1", "Meal2"]  # TODO: load from DB
        )

        # History (sample data)
        initial_history: Iterable[HistoryDay] = [
            ("25/07/2025", [
                {"name": "Meal1", "favorite": True},
                {"name": "Meal2", "favorite": False},
                {"name": "Meal3", "favorite": False},
            ]),
            ("24/07/2025", [
                {"name": "Meal1", "favorite": False},
                {"name": "Meal2", "favorite": True},
                {"name": "Meal3", "favorite": False},
            ]),
        ]
        self.history = HistoryPage(
            go_back=self.go_home,
            on_modify=self.use_history_meal,                 # open New Meal page
            on_delete=self.delete_history_meal,              # remove from history
            on_toggle_fav=self.toggle_favorite_from_history, # star toggle
            initial_history=initial_history
        )

        #Ingredient
        self.new_ingredient = NewIngredientPage(
            go_back=self.go_home,
            on_create=self.on_create_ingredient
        )

        # Add to stack (order doesn’t matter if we use setCurrentWidget)
        for page in (self.home, self.new_meal, self.favorites, self.history, self.new_ingredient):
            self.stack.addWidget(page)

        # Start on Home
        self.go_home()

    # -------------------------------------------------------------------------
    # Navigation (single API: setCurrentWidget)
    # -------------------------------------------------------------------------
    def go_home(self) -> None:
        self.stack.setCurrentWidget(self.home)

    def go_new_meal(self) -> None:
        self.stack.setCurrentWidget(self.new_meal)

    def go_favorites(self) -> None:
        self.stack.setCurrentWidget(self.favorites)

    def go_history(self) -> None:
        self.stack.setCurrentWidget(self.history)
    
    def go_new_ingredient(self):
        self.stack.setCurrentWidget(self.new_ingredient)

    # -------------------------------------------------------------------------
    # Actions / Callbacks
    # -------------------------------------------------------------------------
    def on_create_meal(self, payload):
        # Insert into DB, clear NewMeal form if needed, etc.
        print("CREATE MEAL payload:", payload)
        self.go_home()

    def use_favorite_in_new_meal(self, meal_name: str) -> None:
        print(f"Use favorite: {meal_name} -> New Meal page")
        # TODO: prefill self.new_meal with favorite's ingredients
        self.go_new_meal()

    def delete_favorite(self, meal_name: str) -> None:
        # Remove from DB/store; FavoritesPage removes its own UI row already
        print(f"Delete favorite: {meal_name}")

    def use_history_meal(self, meal_name: str) -> None:
        print("Modify meal via New Meal page:", meal_name)
        # TODO: load meal snapshot by name/date into NewMealPage
        self.go_new_meal()

    def delete_history_meal(self, date_str: str, meal_name: str) -> None:
        print(f"Delete from history: {date_str} – {meal_name}")
        # TODO: remove from DB then refresh:
        # self.history.set_history(updated_days)

    def toggle_favorite_from_history(self, meal_name: str, is_favorite: bool) -> None:
        print(f"Toggle favorite {meal_name} -> {is_favorite}")
        # TODO: write to favorites store

    def on_create_ingredient(self, payload):
        # TODO: insert into DB via your service/repo layer
        print("CREATE INGREDIENT:", payload)
        # Optionally clear form or navigate away
        # self.new_ingredient.clear_form()
        self.go_home()

# -------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    w = App()
    w.resize(1000, 680)
    w.show()
    sys.exit(app.exec())
