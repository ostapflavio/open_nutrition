from fastapi import FastAPI
from src.api.routers import meals, stats
app = FastAPI()
app.include_router(meals.router)
app.include_router(stats.router)
@app.get("/")
async def hello_world():
    return {"message": "hello world!"}