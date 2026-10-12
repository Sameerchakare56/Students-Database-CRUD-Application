# Students Database CRUD Application (+ Ollama AI Extension)

> **Python Backend Development Project | EWB Edu Tech Pvt. Ltd.**

A production-grade Python backend application built with **FastAPI** and **SQLite** to manage student records via full CRUD (Create, Read, Update, Delete) operations. Includes a modern Glassmorphism Web Dashboard and an optional **Local Ollama AI Extension** to query student records in natural language.

---

## 🌟 Key Features

1. **Mandatory CRUD Operations**:
   - **Create**: Add student records with input validation (Email, Phone, Date formats, unique Student ID generation).
   - **Read**: List students with pagination, search query filtering (Name, Code, Course, Email), and profile retrieval by ID or Code.
   - **Update**: Modify student details via full (`PUT`) or partial (`PATCH`) update routes.
   - **Delete**: Remove student records permanently from the SQLite persistent database.

2. **Optional Bonus: Local AI with Ollama**:
   - Natural language database query endpoint (`POST /api/ai/query`).
   - Grounds Ollama models (e.g., `llama3.2:1b`) using actual database records context.
   - Graceful fallback mechanism if local Ollama service is offline.

3. **Interactive Web Dashboard**:
   - Responsive Glassmorphism UI built with Vanilla HTML, CSS, and JS.
   - Dynamic data table, statistics cards, modal dialogs, course filtering, and AI Chat tab.

4. **Automated Testing & Seed Tools**:
   - Complete `pytest` test suite (`tests/test_students.py`).
   - One-click demo data seeding script (`create_seed_data.py`).

---

## 📁 Project Structure

```
Students Database CRUD Application/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry & static files hosting
│   ├── database.py          # SQLite engine & SQLAlchemy session setup
│   ├── models.py            # SQLAlchemy database models (Student)
│   ├── schemas.py           # Pydantic v2 validation models
│   ├── crud.py              # Database access functions & context builder
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py    # Ollama HTTP client & fallback engine
│   └── routers/
│       ├── __init__.py
│       ├── students.py      # CRUD endpoints (/api/students)
│       └── ai.py            # AI extension endpoint (/api/ai/query)
├── static/
│   ├── index.html           # Modern Glassmorphism Web Dashboard UI
│   ├── css/
│   │   └── styles.css       # Premium styles, animations, dark theme
│   └── js/
│       └── app.js           # Frontend interactive application logic
├── tests/
│   ├── __init__.py
│   └── test_students.py     # Pytest automated test suite
├── create_seed_data.py       # Standalone seed script
├── requirements.txt         # Project dependencies
├── run.py                   # Server launcher
└── README.md                # Documentation
```

---

## ⚙️ Prerequisites & Installation

### 1. Prerequisites
- **Python 3.9+** installed on your system.
- *(Optional)* **Ollama** installed with `llama3.2:1b` model pulled (`ollama pull llama3.2:1b`) for local LLM execution.

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone <your-repository-url>
cd "Students Database CRUD Application"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Application

### Option 1: Quick Launcher Script
```bash
python run.py
```

### Option 2: Direct Uvicorn Command
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running:
- 🌐 **Web Application Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📑 **Swagger Interactive API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📖 **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📊 API Endpoints Reference

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `POST` | `/api/students` | Add a new student record |
| `GET` | `/api/students` | List all students (supports `search`, `course`, `skip`, `limit`) |
| `GET` | `/api/students/{identifier}` | View student details by numeric ID or student code (e.g. `STU-1001`) |
| `PUT` / `PATCH` | `/api/students/{identifier}` | Update existing student record details |
| `DELETE` | `/api/students/{identifier}` | Delete a student record permanently |
| `POST` | `/api/students/seed/demo` | Seed initial dummy student records |
| `POST` | `/api/ai/query` | Natural-language query using Ollama grounded DB context |
| `GET` | `/api/health` | Application status health check |

---

## 🧪 Testing & Verification

Run the automated test suite with `pytest`:
```bash
pytest -v
```

All 7 test cases verify:
- Successful creation, email validation, and duplicate rejection.
- Database query filtering and search behavior.
- Retrieval by ID and code.
- Full & partial update operations.
- Record deletion and 404 missing record handling.
- AI query endpoint payload formatting.

---

## 🤖 Ollama AI Extension Setup (Optional Bonus)

To enable local AI inference with Ollama:
1. Download Ollama from [ollama.com](https://ollama.com).
2. Pull the lightweight model:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Start the Ollama server:
   ```bash
   ollama serve
   ```
4. Open the **Ollama AI Assistant** tab in the Web Dashboard or send requests to `POST /api/ai/query`.

---

## 🔒 Security & Best Practices
- **No Direct SQL Execution**: Natural language queries do not directly construct or execute raw SQL strings. Relevant context is structured safely in Python.
- **Dummy Data**: Seed scripts generate dummy demonstration data. No real personal identifiable information (PII) is included.

---

