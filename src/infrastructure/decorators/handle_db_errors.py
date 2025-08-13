from functools import wraps
from typing import Callable
from sqlalchemy import exc as exc
from sqlalchemy.orm import exc as exc_orm
from src.domain.errors import NotFound, DomainError

def handle_db_errors(
    entity: str = "Ingredient"):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try: 
                return func(*args, **kwargs)
            
            # SERVER: database connectivity issue 
            except exc.OperationalError as e:
                pass

            # CLIENT: deterministic data conflicts (unique / fk / check)
            except exc.IntegrityError as e:
                raise Data
            
            # CLIENT: bad data sent 
            except exc.DataError as e:
                pass

            # PROGRAMMER: bad SQL statement 
            except exc.ProgrammingError as e:
                pass

            # SERVER: connection closed 
            except exc.InterfaceError as e:
                pass
            
            # SERVER: connection pool exhausted and waited longer than pool_timeout
            except exc.TimeoutError as e:
                pass

            # SERVER: lost the underlying DB connection (server restart, network glitch, idle timeout)
            except exc.DisconnectionError as e:
                pass

            # PROGRAMMER: failed to generate valid SQL from SQLAlchemy expression
            except exc.CompileError as e:
                pass

            # CLIENT: found 0 rows when exactly one was expected
            except exc.NoResultFound as e:
                pass

            # PROGRAMMER: error during statement execution at the ORM/Core boundary
            except exc.StatementError as e:
                pass

            # CLIENT: found >1 rows when exactly one was expected
            except exc.MultipleResultsFound as e:
                pass
            # PROGRAMMER: accessed a lazy-loaded attribute on an object after session was closed 
            except exc_orm.DetachedInstanceError as e:
                pass

            # PROGRAMMER: tried to add / delete an object whose class wasn't mapped to any table 
            except exc_orm.UnmappedInstanceError as e:
                pass


