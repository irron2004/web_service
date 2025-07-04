from app.db import engine
from app.models import Base

def create_tables():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)
    print("데이터베이스 테이블이 생성되었습니다!")

if __name__ == "__main__":
    create_tables() 