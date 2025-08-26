from fastapi import FastAPI
from routers import meals
app = FastAPI()

@app.get("/")
async def hello_world():
    return {"message": "hello world!"}