from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated
from fastapi import Depends

DATABASE_URL = 'sqlite:///./app.db'
engine = create_engine(
    DATABASE_URL, 
    connect_args = {'check_same_thread': False}
)

SessionLocal = sessionmaker(bind = engine, autocommit = False, autoflush = False)

def get_db():
    db = SessionLocal()
    try: 
        yield db 
    except:
        db.rollback()
        raise
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]