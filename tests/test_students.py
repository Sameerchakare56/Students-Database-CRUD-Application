import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# In-memory SQLite database with StaticPool for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Reset in-memory SQLite tables before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_student_success():
    payload = {
        "student_code": "STU-9999",
        "name": "Test Student",
        "email": "test@example.com",
        "phone": "+91 99999 88888",
        "dob": "2002-01-01",
        "course": "Computer Science",
        "gpa": 3.75
    }
    response = client.post("/api/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Student"
    assert data["student_code"] == "STU-9999"
    assert data["email"] == "test@example.com"
    assert data["id"] is not None


def test_create_student_duplicate_email():
    payload = {
        "name": "Student One",
        "email": "duplicate@example.com",
        "phone": "+91 99999 88888",
        "dob": "2002-01-01"
    }
    res1 = client.post("/api/students", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/students", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_get_students_list_and_filter():
    client.post("/api/students", json={
        "name": "Alice Smith",
        "email": "alice@example.com",
        "phone": "+1 555-0100",
        "dob": "2003-05-12",
        "course": "Data Science"
    })
    client.post("/api/students", json={
        "name": "Bob Jones",
        "email": "bob@example.com",
        "phone": "+1 555-0101",
        "dob": "2002-09-20",
        "course": "Electrical Engineering"
    })

    # List all
    res = client.get("/api/students")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert len(data["students"]) == 2

    # Filter by course
    res_filter = client.get("/api/students?course=Data Science")
    assert res_filter.status_code == 200
    assert res_filter.json()["total"] == 1
    assert res_filter.json()["students"][0]["name"] == "Alice Smith"


def test_get_student_by_id_and_code():
    res = client.post("/api/students", json={
        "student_code": "STU-7001",
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "phone": "+1 555-0102",
        "dob": "2001-12-04"
    })
    created = res.json()
    db_id = created["id"]

    # Retrieve by numeric ID
    res_id = client.get(f"/api/students/{db_id}")
    assert res_id.status_code == 200
    assert res_id.json()["name"] == "Charlie Brown"

    # Retrieve by code
    res_code = client.get("/api/students/STU-7001")
    assert res_code.status_code == 200
    assert res_code.json()["email"] == "charlie@example.com"


def test_update_student():
    res = client.post("/api/students", json={
        "name": "David Miller",
        "email": "david@example.com",
        "phone": "+1 555-0103",
        "dob": "2000-04-18",
        "course": "Math"
    })
    db_id = res.json()["id"]

    update_payload = {
        "course": "Advanced Mathematics",
        "gpa": 3.90
    }
    res_update = client.put(f"/api/students/{db_id}", json=update_payload)
    assert res_update.status_code == 200
    updated = res_update.json()
    assert updated["course"] == "Advanced Mathematics"
    assert updated["gpa"] == 3.90


def test_delete_student():
    res = client.post("/api/students", json={
        "name": "Eva Green",
        "email": "eva@example.com",
        "phone": "+1 555-0104",
        "dob": "2002-08-30"
    })
    db_id = res.json()["id"]

    # Delete
    res_del = client.delete(f"/api/students/{db_id}")
    assert res_del.status_code == 200

    # Verify 404
    res_get = client.get(f"/api/students/{db_id}")
    assert res_get.status_code == 404


def test_ai_query_endpoint():
    # Seed a student
    client.post("/api/students", json={
        "name": "Frank White",
        "email": "frank@example.com",
        "phone": "+1 555-0105",
        "dob": "2004-10-10",
        "course": "Cyber Security"
    })

    res = client.post("/api/ai/query", json={"question": "How many total students are there?"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "ollama_status" in data


def test_read_root_dashboard():
    response = client.get("/")
    assert response.status_code == 200


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

