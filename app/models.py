from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Student(Base):
    """SQLAlchemy model representing a student record in SQLite."""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    dob = Column(String(10), nullable=False)  # ISO format: YYYY-MM-DD
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(String(10), nullable=True)  # ISO format: YYYY-MM-DD
    gpa = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

