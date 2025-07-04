from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="student")
    locale = Column(String, default="ko")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    total_ms = Column(Integer)
    correct_cnt = Column(Integer)
    user = relationship("User")

class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    left = Column(Integer)
    right = Column(Integer)
    answer = Column(Integer)
    chosen = Column(Integer, nullable=True)
    is_correct = Column(Boolean, default=False)
    attempt_no = Column(Integer, default=1)
    session = relationship("Session")

class ParentAlert(Base):
    __tablename__ = "parent_alerts"
    id = Column(Integer, primary_key=True, index=True)
    parent_email = Column(String)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    sent_at = Column(DateTime)
    session = relationship("Session") 