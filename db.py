import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv()

class Base(DeclarativeBase):
    pass

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise RuntimeError("DB_URL is not configured")

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    pool_recycle=280,
    pool_size=5,
    max_overflow=5,
    pool_timeout=30,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)