class MealService:
    def add_meal(
            self, 
            entries: list[tuple[int, float]],       # (ingredient_id, grams)
            timestamp: datetime | None = None, 
            is_favorite: bool = False) -> Meal:

        pass

    def relog_from_history(
            self, 
            source_meal_id: int,
            timestamp: datetime | None = None) -> Meal:
        pass

    def relog_favorite(
            self,
            favorite_meal_id: int, 
            timestamp: datetime | None = None) -> Meal:
        pass

class StatsService:
    def totals_for_range(self, time_range: DataRange) -> SummaryStats:
        pass

    def daily_breakdown(self, time_range: DataRange) -> dict[str, MacroTotals]:
        pass
    
    def weekly_summar(self) -> SummaryStats:
        pass 

    def compare(self, date1: datetime, date2: datetime):
        pass

class IngredientService: 
    def search(self, query: str, source: IngredientSource | None) -> Ingredient:
        pass

    def create_custom(self, ingredient: Ingredient) -> Ingredient:
        pass

class MacroAnalyzer:
    def compare_stats(self, current_stats: MacroTotals):
        pass


