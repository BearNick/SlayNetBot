# app/storage.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine("sqlite:///bot.db", echo=False, future=True)
Session = sessionmaker(bind=engine, future=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    plan_code = Column(String, default="T1")
    current_key_id = Column(String, nullable=True)
    current_key_secret = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, index=True)
    code = Column(String, index=True)           # уникальный код (в сообщении доната)
    amount = Column(Float)
    currency = Column(String, default="RUB")
    status = Column(String, default="pending")  # pending/paid
    created_at = Column(DateTime, default=datetime.utcnow)

class KV(Base):
    __tablename__ = "kv"
    key = Column(String, primary_key=True)
    value = Column(Text)

def init_db():
    Base.metadata.create_all(engine)

def days_left(user: User) -> int:
    if not user.expires_at:
        return 0
    delta = user.expires_at - datetime.utcnow()
    return max(0, delta.days)
