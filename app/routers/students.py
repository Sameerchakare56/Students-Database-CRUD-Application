from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(
    prefix="/api/students",
    tags=["Students CRUD"]
)


@router.post(
    "",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student record"
)
def create_student(
    student_in: schemas.StudentCreate,
    db: Session = Depends(get_db)
):
    """Add a new student record to the SQLite database with validation."""
    # Check duplicate email
    if crud.get_student_by_email(db, student_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with email '{student_in.email}' already exists."
        )

    # Check duplicate student_code if provided
    if student_in.student_code and crud.get_student_by_code(db, student_in.student_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with code '{student_in.student_code}' already exists."
        )

    return crud.create_student(db, student_in)


@router.get(
    "",
    response_model=schemas.StudentListResponse,
    summary="List or filter all student records"
)
def list_students(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    search: Optional[str] = Query(None, description="Search term for name, email, course, or student code"),
    course: Optional[str] = Query(None, description="Filter by course name"),
    db: Session = Depends(get_db)
):
    """List all students with search, filter, and pagination support."""
    students, total = crud.get_students(
        db, skip=skip, limit=limit, search=search, course=course
    )
    return schemas.StudentListResponse(
        total=total,
        page=(skip // limit) + 1,
        limit=limit,
        students=students
    )


@router.get(
    "/{identifier}",
    response_model=schemas.StudentResponse,
    summary="Retrieve details of a single student by ID or Student Code"
)
def get_student(
    identifier: str,
    db: Session = Depends(get_db)
):
    """Fetch student profile by integer ID (e.g., 1) or student_code (e.g., STU-1001)."""
    student = crud.get_student_by_code_or_id(db, identifier)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record '{identifier}' not found."
        )
    return student


@router.put(
    "/{identifier}",
    response_model=schemas.StudentResponse,
    summary="Update an existing student record (Full or Partial)"
)
@router.patch(
    "/{identifier}",
    response_model=schemas.StudentResponse,
    summary="Update an existing student record (Partial)"
)
def update_student(
    identifier: str,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    """Modify details of an existing student record."""
    db_student = crud.get_student_by_code_or_id(db, identifier)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record '{identifier}' not found."
        )

    # Check email uniqueness if email is changing
    if student_update.email and student_update.email != db_student.email:
        existing = crud.get_student_by_email(db, student_update.email)
        if existing and existing.id != db_student.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{student_update.email}' is already in use by another student."
            )

    return crud.update_student(db, db_student, student_update)


@router.delete(
    "/{identifier}",
    response_model=schemas.StudentResponse,
    summary="Delete a student record"
)
def delete_student(
    identifier: str,
    db: Session = Depends(get_db)
):
    """Remove student record permanently from SQLite database."""
    db_student = crud.get_student_by_code_or_id(db, identifier)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record '{identifier}' not found."
        )
    return crud.delete_student(db, db_student)


@router.post(
    "/seed/demo",
    summary="Seed dummy student data for demonstration",
    status_code=status.HTTP_200_OK
)
def seed_demo_students(db: Session = Depends(get_db)):
    """Populate database with sample student records if database is empty."""
    dummy_records = [
        {
            "student_code": "STU-1001",
            "name": "Aarav Sharma",
            "email": "aarav.sharma@example.com",
            "phone": "+91 98765 43210",
            "dob": "2002-05-14",
            "course": "Computer Science & Engineering",
            "address": "42 MG Road, Bengaluru, KA",
            "enrollment_date": "2023-08-01",
            "gpa": 3.85
        },
        {
            "student_code": "STU-1002",
            "name": "Ananya Verma",
            "email": "ananya.v@example.com",
            "phone": "+91 98123 45678",
            "dob": "2003-11-20",
            "course": "Data Science & AI",
            "address": "15 Park Street, Kolkata, WB",
            "enrollment_date": "2023-08-01",
            "gpa": 3.92
        },
        {
            "student_code": "STU-1003",
            "name": "Rohan Mehta",
            "email": "rohan.mehta@example.com",
            "phone": "+91 97111 22334",
            "dob": "2001-03-08",
            "course": "Information Technology",
            "address": "88 Bandra Reclamation, Mumbai, MH",
            "enrollment_date": "2022-08-01",
            "gpa": 3.45
        },
        {
            "student_code": "STU-1004",
            "name": "Priya Patel",
            "email": "priya.patel@example.com",
            "phone": "+91 99000 88776",
            "dob": "2004-01-15",
            "course": "Data Science & AI",
            "address": "204 C.G. Road, Ahmedabad, GJ",
            "enrollment_date": "2024-01-10",
            "gpa": 3.70
        },
        {
            "student_code": "STU-1005",
            "name": "Vikram Singh",
            "email": "vikram.singh@example.com",
            "phone": "+91 96555 44332",
            "dob": "2006-07-22",
            "course": "Cyber Security",
            "address": "12 Civil Lines, Jaipur, RJ",
            "enrollment_date": "2024-08-15",
            "gpa": 3.60
        }
    ]

    added_count = 0
    for data in dummy_records:
        if not crud.get_student_by_email(db, data["email"]):
            crud.create_student(db, schemas.StudentCreate(**data))
            added_count += 1

    return {
        "message": f"Seeding complete. {added_count} new dummy student records created.",
        "total_records": db.query(crud.Student).count()
    }
