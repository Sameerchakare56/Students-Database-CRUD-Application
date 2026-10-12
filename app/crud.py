from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


def generate_next_student_code(db: Session) -> str:
    """Generate next available student code like STU-1001, STU-1002."""
    max_id = db.query(func.max(Student.id)).scalar() or 0
    return f"STU-{1000 + max_id + 1}"


def get_student(db: Session, student_id: int) -> Optional[Student]:
    """Retrieve a single student record by primary key ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_code_or_id(db: Session, identifier: str) -> Optional[Student]:
    """Retrieve student by integer ID or string student_code (e.g. STU-1001 or 1)."""
    if identifier.isdigit():
        student = get_student(db, int(identifier))
        if student:
            return student
    return db.query(Student).filter(Student.student_code == identifier).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Find student by email address."""
    return db.query(Student).filter(Student.email == email).first()


def get_student_by_code(db: Session, student_code: str) -> Optional[Student]:
    """Find student by unique student_code."""
    return db.query(Student).filter(Student.student_code == student_code).first()


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    course: Optional[str] = None
) -> Tuple[List[Student], int]:
    """Retrieve list of students with filtering, search query, and pagination."""
    query = db.query(Student)

    if course:
        query = query.filter(Student.course.ilike(f"%{course}%"))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Student.name.ilike(search_pattern),
                Student.email.ilike(search_pattern),
                Student.student_code.ilike(search_pattern),
                Student.course.ilike(search_pattern)
            )
        )

    total = query.count()
    students = query.order_by(Student.id.desc()).offset(skip).limit(limit).all()
    return students, total


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """Create and persist a new student record."""
    student_data = student_in.model_dump()
    
    if not student_data.get("student_code"):
        student_data["student_code"] = generate_next_student_code(db)

    db_student = Student(**student_data)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, db_student: Student, student_update: StudentUpdate) -> Student:
    """Update existing student details (partial or full)."""
    update_data = student_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, db_student: Student) -> Student:
    """Delete a student record from database."""
    db.delete(db_student)
    db.commit()
    return db_student


def get_database_summary_context(db: Session) -> str:
    """Generate a clean, grounded text context of student records for Ollama AI querying."""
    total_students = db.query(Student).count()
    if total_students == 0:
        return "Database status: Currently empty (0 students enrolled)."

    students = db.query(Student).order_by(Student.id.asc()).all()
    
    # Calculate statistics
    courses_count = {}
    for s in students:
        c = s.course or "Unassigned"
        courses_count[c] = courses_count.get(c, 0) + 1

    lines = [
        f"Total Students: {total_students}",
        f"Courses Summary: {courses_count}",
        "Student Records List:"
    ]

    for s in students:
        lines.append(
            f"- ID: {s.student_code} (Database ID: {s.id}), Name: {s.name}, Email: {s.email}, "
            f"Phone: {s.phone}, DOB: {s.dob}, Course: {s.course or 'N/A'}, "
            f"Enrollment Date: {s.enrollment_date or 'N/A'}, GPA: {s.gpa if s.gpa is not None else 'N/A'}"
        )

    return "\n".join(lines)
