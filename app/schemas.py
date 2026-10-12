from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class StudentBase(BaseModel):
    student_code: Optional[str] = Field(None, description="Unique Student ID (e.g. STU-1001). Auto-generated if omitted.")
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the student")
    email: EmailStr = Field(..., description="Unique contact email address")
    phone: str = Field(..., min_length=7, max_length=20, description="Contact phone number")
    dob: str = Field(..., description="Date of birth in YYYY-MM-DD format")
    course: Optional[str] = Field(None, max_length=100, description="Enrolled course or program")
    address: Optional[str] = Field(None, max_length=255, description="Residential address")
    enrollment_date: Optional[str] = Field(None, description="Enrollment date in YYYY-MM-DD format")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="Grade Point Average (0.0 to 4.0)")

    @field_validator("dob", "enrollment_date")
    def validate_date_format(cls, v):
        if v is None:
            return v
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    student_code: Optional[str] = None
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=7, max_length=20)
    dob: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)

    @field_validator("dob", "enrollment_date")
    def validate_date_format(cls, v):
        if v is None:
            return v
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class StudentResponse(StudentBase):
    id: int
    student_code: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)



class StudentListResponse(BaseModel):
    total: int
    page: int
    limit: int
    students: List[StudentResponse]


class AIQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Natural language question about student data")
    model: Optional[str] = Field("llama3.2:1b", description="Ollama model name to use")


class AIQueryResponse(BaseModel):
    question: str
    answer: str
    context_used: str
    model_used: str
    ollama_status: str  # "online" or "offline_fallback"
