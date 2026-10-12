import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.database import engine, Base, SessionLocal
from app.routers import students, ai
from app import crud, schemas

# Initialize SQLite tables automatically
Base.metadata.create_all(bind=engine)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Auto-seed sample student data on first run if database is empty."""
    db = SessionLocal()
    try:
        if db.query(crud.Student).count() == 0:
            students.seed_demo_students(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Students Database CRUD Application API",
    description=(
        "Production-ready FastAPI backend with persistent SQLite storage for Student Records management. "
        "Includes optional Local AI Extension with Ollama context grounding."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(students.router)
app.include_router(ai.router)

# Static files directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def read_root():
    """Serve web application UI dashboard."""
    index_file = os.path.normpath(os.path.join(static_dir, "index.html"))
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({
        "status": "online",
        "message": "Students Database CRUD API is running. Access API Docs at /docs",
        "documentation": "/docs"
    })



@app.get("/api/health", tags=["Health"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "database": "SQLite connected",
        "service": "Students Database CRUD API"
    }
