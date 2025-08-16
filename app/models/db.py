from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./shopify_insights.db")

engine = create_async_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()
