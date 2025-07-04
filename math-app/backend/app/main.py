from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api

app = FastAPI(title="Math App API", version="1.0.0")

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Hello, Math App!", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Server is running"} 