import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Support database URL from environment variable, default to SQLite in current directory
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./food_order.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},  # Required for SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    """All models inherit from this class so SQLAlchemy knows about them."""
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
