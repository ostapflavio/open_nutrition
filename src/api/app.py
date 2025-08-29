from fastapi import FastAPI
from src.api.routers import meals
app = FastAPI()
app.include_router(meals.router)
@app.get("/")
async def hello_world():
    return {"message": "hello world!"}