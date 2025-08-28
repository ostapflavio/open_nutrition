import sys, pathlib
import os, shutil

# add project root to sys.path (from src/tests/ -> up to project root)
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
import pytest 
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 

from src.data.database_models import Base, IngredientModel

@pytest.fixture
def session(tmp_path, request):
    """
    Easiest setup: isolated file-based SQLite DB per test.
    """
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}", future = True)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind = engine, future = True)

    with SessionLocal() as s:
        yield s 

    # Persist a copy for insepection later 
    if os.getenv("KEEP_TEST_DB") == "1":
        outdir = pathlib.Path.cwd() / ".pytest_dbs"
        outdir.mkdir(exist_ok=True)
        shutil.copy(db_file, outdir / f"{request.node.name}.db")
    
@pytest.fixture
def seed_ingredients(session):
    """
    Insert multiple ingredients for search / update / delete tests.
    """

    rows = [
        IngredientModel(
            name = "Apple",
            fats_per_100g = 0.2, proteins_per_100g = 0.3, carbs_per_100g=14.0, kcal_per_100g = 100.0
        ),
       IngredientModel(
            name = "Banana",
            fats_per_100g = 0.2, proteins_per_100g = 0.3, carbs_per_100g=14.0, kcal_per_100g = 160.0
        ),
       IngredientModel(
            name = "Mango",
            fats_per_100g = 0.2, proteins_per_100g = 0.3, carbs_per_100g=14.0, kcal_per_100g = 60.0
        ),
        IngredientModel(
            name = "Chicken Breast",
            fats_per_100g = 3.6, proteins_per_100g = 31.0, carbs_per_100g=10.0, kcal_per_100g = 50.0
        ),
        IngredientModel(
            name = "almond milk",
            fats_per_100g = 3.6, proteins_per_100g = 0.5, carbs_per_100g=70.5, kcal_per_100g = 60.0
        ),
        IngredientModel(
            name = "Egg",
            fats_per_100g = 11.0, proteins_per_100g = 6.0, carbs_per_100g=1.1, kcal_per_100g = 70.0
        ),
    ]

    session.add_all(rows)
    session.commit()

    for r in rows:
        session.refresh(r)

    by_name = {r.name: r for r in rows}
    return by_name, rows