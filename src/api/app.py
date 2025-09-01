from fastapi import FastAPI
from src.api.routers import meals, ingredients, favorites
app = FastAPI()
app.include_router(meals.router)

app.include_router(ingredients.router)
app.include_router(favorites.router)
@app.get("/")
async def hello_world():
    return {"message": "hello world!"}