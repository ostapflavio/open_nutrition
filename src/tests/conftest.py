import pytest 
from sqlalchemy.orm import sessionmaker 
from sqlalchemy import create_engine 
from src.data.database_models import Base 
from src.infrastructure.repositories.ingredient_repo import IngredientRepo
import os, sys

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo = True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    yield Session()

print("PYTHONPATH:", sys.path)
