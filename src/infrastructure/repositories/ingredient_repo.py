from src.domain import IngredientSource, Ingredient

class IngredientRepo:
    """
    A repo to work with the database, with the ingredients table.  
    """
    
    def __init__(self, session):
        # define a global session, such that we can do operations with the database 
        self.session = session 

    def get_by_id(self, id: int) -> Ingredient:
        """Find the ingredient by id. """
        return self.session.get(Ingredient, id)

    
    def find_by_name(self, query: str, limit: int = 10) -> list[Ingredient]:
        return self.session.query(Ingredient).filter(Ingredient.name.ilike(f"%{query}%")).limit(10).all()

    def create(
            self, 
            name: str, 
            kcal_per_100g: float, 
            carbs_per_100g: float, 
            proteins_per_100g: float, 
            fats_per_100g: float, 
            source: IngredientSource = IngredientSource.CUSTOM,
            external_id: int = -1
    ) -> Ingredient:
        """Create a new ingredient. """
        ingredient = Ingredient(
                        name = name, 
                        kcal_per_100g = kcal_per_100g, 
                        carbs_per_100g = carbs_per_100g, 
                        proteins_per_100g = proteins_per_100g, 
                        fats_per_100g = fats_per_100g,
                        source = source.value, 
                        external_id = external_id
                    )
        self.session.add(ingredient)
        self.session.commit()
        return ingredient


     
    def update(self, identifier: int | str, **kwargs) -> Ingredient:
        """Alter an existing ingredient using it's name or id. NOTE: when we search by name, we take the first ingredient as the first one that we need to alter.  """
        # determine if we search by id or name 
        if isinstance(identifier, int):
            ingredient = self.session.query(Ingredient).filter_by(id = identifier).first()
        else:
            ingredient = self.session.query(Ingredient).filter_by(name = identifier).first()

        if not ingredient:
            raise IngredientNotFound(f"Ingredient with {'ID' if isinstance(identifier, int) else 'name'} '{identifier}' not found.")
        
        for key, value in kwargs.items():
            if hasattr(ingredient, key) and value is not None:
                setattr(ingredient, key, value)
        
        self.session.commit()
        return ingredient
    
    def delete(self, id: int) -> None:
        """Delete an ingredient using it's id. """
        ingredient = self.session.get(Ingredient, id)
        if not ingredient:
            raise IngredientNotFound(f"Ingredient with ID '{id}' not found.")

        self.session.delete(ingredient)
        self.session.commit()
