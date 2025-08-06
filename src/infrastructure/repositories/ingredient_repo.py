from src.domain import IngredientSource, Ingredient
from src.domain.errors import IngredientNotFound
from src.data.database_models import IngredientModel
from sqlalchemy import func



class IngredientRepo:
    """
    A repo to work with the database, with the ingredients table.  
    """
    def _to_domain(self, row: IngredientModel) -> Ingredient:
        if row is None:
            raise IngredientNotFound("Ingredient not found.")

        # convert to enum 
        source = row.source 

        # type check 
        if not isinstance(source, IngredientSource):
            source = IngredientSource(source)

        return Ingredient(
            id=row.id,
            name=row.name,
            fats_per_100g=row.fats_per_100g,
            proteins_per_100g=row.proteins_per_100g,
            carbs_per_100g=row.carbs_per_100g,
            kcal_per_100g=row.kcal_per_100g,
            source=source,
            external_id=row.external_id,
        )    

    def __init__(self, session):
        # define a global session, such that we can do operations with the database 
        self.session = session 

    def get_by_id(self, id: int) -> Ingredient:
        """Find the ingredient by id. """
        row: IngredientModel = self.session.get(IngredientModel, id)
        return self._to_domain(row)


    
    def find_by_name(self, query: str, limit: int = 10) -> list[Ingredient]:
        rows: list[IngredientModel] = (
            self.session.query(IngredientModel)
            .filter(func.lower(IngredientModel.name).like(f"%{query.lower()}%"))
            .limit(limit)
            .all()
        )

        return [self._to_domain(r) for r in rows]


    def create(self, domain_ingredient: Ingredient) -> Ingredient:
        """Create a new ingredient. """
        ingredient = IngredientModel(
                        name = domain_ingredient.name, 
                        kcal_per_100g = domain_ingredient.kcal_per_100g, 
                        carbs_per_100g = domain_ingredient.carbs_per_100g, 
                        proteins_per_100g = domain_ingredient.proteins_per_100g, 
                        fats_per_100g = domain_ingredient.fats_per_100g,
                        source = domain_ingredient.source.value, 
                        external_id = domain_ingredient.external_id
                    )
        self.session.add(ingredient)
        self.session.commit()
        self.session.refresh(ingredient)
        return self._to_domain(ingredient)


     
    def update(self, identifier: int | str, **kwargs) -> Ingredient:
        """Alter an existing ingredient using it's name or id. NOTE: when we search by name, we take the first ingredient as the first one that we need to alter.  """
        # determine if we search by id or name 
        if isinstance(identifier, int):
            ingredient: IngredientModel = self.session.query(IngredientModel).filter_by(id = identifier).first()
        else:
            ingredient: IngredientModel = self.session.query(IngredientModel).filter_by(name = identifier).first()

        if not ingredient:
            raise IngredientNotFound(f"Ingredient with {'ID' if isinstance(identifier, int) else 'name'} '{identifier}' not found.")
        
        if "source" in kwargs and kwargs["source"] is not None:
            source = kwargs.pop("source")
            ingredient.source = source.value if isinstance(source, IngredientSource) else str(source) 
        updatable = {
            "name",
            "kcal_per_100g",
            "carbs_per_100g",
            "proteins_per_100g",
            "fats_per_100g",
            "external_id",
        }
        for key, value in kwargs.items():
            if key in updatable and value is not None:
                setattr(ingredient, key, value)
        
        self.session.commit()
        self.session.refresh(ingredient) # keep the object up-to date 
        return self._to_domain(ingredient)
    
    def delete(self, id: int) -> None:
        """Delete an ingredient using it's id. """
        ingredient: IngredientModel = self.session.get(IngredientModel, id)
        if not ingredient:
            raise IngredientNotFound(f"Ingredient with ID '{id}' not found.")

        self.session.delete(ingredient)
        self.session.commit()