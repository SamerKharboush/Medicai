from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import Base, engine, SessionLocal
from app.models.doctor import Doctor
from app.models.patient import Patient, ClinicalRecord
from app.models.patient_assignment import PatientAssignment
from app.db.test_data import create_test_data, test_doctors

def init_db(db: Session) -> None:
    print("Dropping all tables...")
    # Drop all tables with cascade
    with engine.connect() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        connection.commit()
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Creating test data...")
    try:
        create_test_data(db)
        print("Test data created successfully!")
    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
        raise
    
    # Create test doctors
    for doctor_data in test_doctors:
        doctor = Doctor(**doctor_data)
        db.add(doctor)
    
    try:
        db.commit()
    except Exception as e:
        print(f"Error creating test doctors: {e}")
        db.rollback()
        raise

def main() -> None:
    init_db()

if __name__ == "__main__":
    main()
