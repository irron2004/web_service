from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mbti.db")
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)

def get_session():
    with SessionLocal() as session:
        yield session

def init_db() -> None:
    SQLModel.metadata.create_all(engine) 