import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import Base, User, Patient, ClinicalHistory
from app.core.auth import get_password_hash

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create test user
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create test patients
        patients = [
            Patient(
                medical_record_number="MRN001",
                full_name="John Doe",
                date_of_birth=datetime(1980, 1, 1),
                gender="male"
            ),
            Patient(
                medical_record_number="MRN002",
                full_name="Jane Smith",
                date_of_birth=datetime(1990, 5, 15),
                gender="female"
            )
        ]
        
        for patient in patients:
            db.add(patient)
        db.commit()
        
        # Create test clinical histories
        histories = [
            ClinicalHistory(
                patient_id=1,
                recorded_by_id=1,
                age=42,
                risk_factors=["diabetes", "hypertension"],
                family_history=["Father: Heart Disease"],
                surgical_history=["Appendectomy 2010"],
                transcribed_text="Patient is a 42-year-old male with a history of diabetes and hypertension..."
            ),
            ClinicalHistory(
                patient_id=2,
                recorded_by_id=1,
                age=32,
                risk_factors=["smoking"],
                family_history=["Mother: Breast Cancer"],
                surgical_history=["Tonsillectomy 2000"],
                transcribed_text="Patient is a 32-year-old female with a history of smoking..."
            )
        ]
        
        for history in histories:
            db.add(history)
        db.commit()
        
        print("Database initialized with test data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
