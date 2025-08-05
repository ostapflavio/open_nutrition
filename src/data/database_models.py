from sqlalchemy import (
    Column, Integer, String, Float, func,
    DateTime, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship 

Base = declarative_base()

class MealModel(Base):
    """
    A meal eaten at a specific time.
    """

    __tablename__ = 'history_meals'

    id        = Column(Integer, primary_key = True)
    eaten_at = Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    name      = Column(String(64), nullable = False)

    # one meal -> many entries
    entries = relationship(
        'MealEntry', 
        back_populates = 'meal', 
        cascade = 'all, delete-orphan'
    ) 

   # one meal can be saved as favorite
    favorites = relationship(
        'FavoriteMeal', 
        back_populates = 'meal', 
        cascade = 'all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f"<Meal id={self.id} name = '{self.name}'>"

class MealEntryModel(Base):
    """
    A single ingredient entry inside a meal. 
    """
    __tablename__ = 'meal_entry'

    id            = Column(Integer, primary_key = True)
    meal_id       = Column(Integer, ForeignKey('history_meals.id'), nullable = False, index = True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable = False, index = True)
    grams         = Column(Float, nullable = False)

    meal       = relationship('Meal', back_populates = 'entries')
    ingredient = relationship('Ingredient', back_populates = 'meal_entries')

    __table_args__ = (
        CheckConstraint('grams >= 0', name = 'GRAMS_NOT_NEGATIVE'),
    ) 

    def __repr__(self) -> str:
        return f"<MealEntry id = {self.id} meal_id = {self.meal_id} g = {self.grams}>"

class FavoriteMealModel(Base):
    """
    A user-starred snapshot pointing back to a Meal. 
    """
    __tablename__ = 'favorite_meals'
    id            = Column(Integer, primary_key = True)
    meal_id       = Column(Integer, ForeignKey('history_meals.id'), nullable = False, index = True)
    starred_at    = Column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    name          = Column(String(64), nullable = False)

    meal = relationship('Meal', back_populates = 'favorites')

    __table_args__ = (
        UniqueConstraint("meal_id", name = "UQ_favorite_unique_meal"),
    )

    def __repr__(self) -> str:
        return f"<FavoriteMeal id = {self.id} name = '{self.name}' meal_id = {self.meal_id}"

class IngredientModel(Base):
    __tablename__ = 'ingredients'

    id                   = Column(Integer, primary_key = True)
    name                 = Column(String(64), nullable = False)
    kcal_per_100g        = Column(Float, nullable = False)
    carbs_per_100g       = Column(Float, nullable = False)
    fats_per_100g        = Column(Float, nullable = False)
    proteins_per_100g    = Column(Float, nullable = False)
    source               = Column(String(10), nullable = False)
    external_id          = Column(String(64), nullable = False)

    meal_entries   = relationship('MealEntry', back_populates = 'ingredient')

    __table_args__ = (
        CheckConstraint('kcal_per_100g >= 0', name = 'KCAL_NOT_NEGATIVE'),
        CheckConstraint('carbs_per_100g >= 0', name = 'CARBS_NOT_NEGATIVE'),
        CheckConstraint('fats_per_100g >= 0', name = 'FATS_NOT_NEGATIVE'),
        CheckConstraint('proteins_per_100g >= 0', name = 'PROTEINS_NOT_NEGATIVE'), 
        UniqueConstraint('source', 'external_id', name = 'UQ_ingredient_source_extid'),
    )

    def __repr__(self) -> str:
        return f"<Ingredient id = {self.id} name = '{self.name}'>"