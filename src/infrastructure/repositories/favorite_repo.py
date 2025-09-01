from sqlalchemy import select

from src.domain.domain import Meal
from src.data.database_models import FavoriteMealModel
from src.domain.errors import MealNotFound, FavoriteAlreadyExists
from src.infrastructure.repositories.meal_repo import MealRepo

class FavoriteRepo:
    def __init__(self, session, meal_repo: MealRepo):
        self.session = session 
        self._meal_repo = meal_repo 

    def get(self, favorite_id: int) -> Meal:
        '''Return the meal that is marked as favorite.'''
        favorite: FavoriteMealModel | None = self.session.get(FavoriteMealModel, favorite_id)
        if favorite is None:
            # TODO: Rework the NotFound error 
            raise MealNotFound(message = "Favorite meal was not found!", identifier = favorite_id)

        meal_id: int = favorite.meal_id
        return self._meal_repo.get_by_id(meal_id) 

    def add(self, meal_id: int) -> Meal:    
        ''' Add a new meal to favorite.'''
        domain_meal: Meal = self._meal_repo.get_by_id(meal_id) 

        existing = self.session.query(FavoriteMealModel).filter_by(meal_id = meal_id).first()
        if existing is not None:
            raise FavoriteAlreadyExists(meal_id)

        new_favorite_meal: FavoriteMealModel = FavoriteMealModel(meal_id = meal_id, name = domain_meal.name)
        self.session.add(new_favorite_meal)
        self.session.commit()

        return domain_meal
    
    def delete(self, favorite_id: int) -> None:
        ''' Delete a starred meal. ''' 
        favorite: FavoriteMealModel | None = self.session.get(FavoriteMealModel, favorite_id)
        if favorite is None:
            # TODO: Rework the NotFound error 
            raise MealNotFound(message = "Favorite meal was not found!", identifier = favorite_id)

        self.session.delete(favorite) 
        self.session.commit()

    def update(self, favorite_id: int, domain_meal: Meal) -> Meal:
        ''' Since changing a favorit meals <==> changing the actual meal in history, I will work in the same manner as MealRepo.update()
        pass'''
        favorite: FavoriteMealModel | None = self.session.get(FavoriteMealModel, favorite_id)
        if favorite is None:
            # TODO: Rework the NotFound error 
            raise MealNotFound(message = "Favorite meal was not found!", identifier = favorite_id)

        meal_id: int = favorite.meal_id 
        current_meal: Meal = self._meal_repo.update(meal_id, domain_meal)
        return current_meal

    def search(self, q: str, limit: int =50) -> list[FavoriteMealModel]:
        stmt = (
            select(FavoriteMealModel)
            .where(FavoriteMealModel.name.ilike(f"%{q}%"))
            .order_by(FavoriteMealModel.starred_at.desc())
            .limit(limit)
        )

        return self.session.execute(stmt).scalars().all()