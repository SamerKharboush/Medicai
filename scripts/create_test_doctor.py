import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import date
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.doctor import Doctor
from app.core.security import get_password_hash

def create_test_doctor(db: Session) -> None:
    test_doctor = Doctor(
        email="dr.williams@medicai.com",
        hashed_password=get_password_hash("test123"),
        first_name="John",
        last_name="Williams",
        medical_license_number="ML123456",
        qualifications="MD, PhD",
        specialty="Cardiology",
        subspecialty="Interventional Cardiology",
        years_of_experience=15,
        doctor_type="consultant",
        date_of_birth=date(1975, 1, 1),
        gender="Male",
        contact_number="+1234567890",
        emergency_contact="+1987654321",
        department="Cardiology",
        is_active=True
    )
    
    db.add(test_doctor)
    db.commit()
    print(f"Test doctor created: {test_doctor.email}")

def main() -> None:
    db = SessionLocal()
    try:
        create_test_doctor(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()