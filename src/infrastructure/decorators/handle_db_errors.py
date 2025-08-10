from functools import wraps
from typing import Callable
from src.data.database_models import (
        IngredientModel, 
        MealEntryModel, 
        MealModel, 
        FavoriteMealModel
    )
from sqlalchemy import exc as exc
from sqlalchemy.orm import exc as exc_orm
def handle_db_errors(handle_class = IngredientModel):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try: 
                return func(*args, **kwargs)
            except exc.OperationalError as e:
                pass
            except exc.IntegrityError as e:
                pass
            except exc.DataError as e:
                pass
            except exc.ProgrammingError as e:
                pass
            except exc.InterfaceError as e:
                pass
            except exc.TimeoutError as e:
                pass
            except exc.DisconnectionError as e:
                pass
            except exc.CompileError as e:
                pass
            except exc.NoResultFound as e:
                pass
            except exc.StatementError as e:
                pass
            except exc.MultipleResultsFound as e:
                pass
            except exc_orm.DetachedInstanceError as e:
                pass
            except exc_orm.UnmappedInstanceError as e:
                pass


