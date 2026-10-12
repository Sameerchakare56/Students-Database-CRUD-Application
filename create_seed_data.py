"""
Seed script to populate SQLite database with initial sample student records.
"""
from app.database import SessionLocal, Base, engine
from app.routers.students import seed_demo_students

if __name__ == "__main__":
    print("🌱 Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("🌱 Seeding sample student records...")
        result = seed_demo_students(db)
        print(f"✅ {result['message']}")
        print(f"📊 Total student records in database: {result['total_records']}")
    finally:
        db.close()
