import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database file URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./students.db")

# Create engine with connect_args for SQLite multi-thread compatibility
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db():
    """Dependency that provides a database session for request lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
