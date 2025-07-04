from fastapi import FastAPI
from app import api

app = FastAPI()

app.include_router(api.router)

@app.get("/")
def root():
    return {"message": "Hello, Math App!"} 