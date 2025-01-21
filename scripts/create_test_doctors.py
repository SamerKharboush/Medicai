from datetime import date
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.core.security import get_password_hash
from app.models.doctor import Doctor, DoctorType
import json

def create_test_doctors():
    db = SessionLocal()
    try:
        # Create Consultant Doctor
        consultant = Doctor(
            email="consultant@medicai.com",
            hashed_password=get_password_hash("consultant123"),
            first_name="John",
            last_name="Smith",
            medical_license_number="CON123456",
            qualifications="MD, PhD, FRCS",
            specialty="Cardiology",
            subspecialty="Interventional Cardiology",
            years_of_experience=15,
            doctor_type="consultant",
            date_of_birth=date(1975, 5, 15),
            gender="Male",
            contact_number="+1234567890",
            emergency_contact="+1987654321",
            department="Cardiology",
            office_location="Building A, Floor 3, Room 302",
            consultation_hours=json.dumps({
                "Monday": "9:00-17:00",
                "Wednesday": "9:00-17:00",
                "Friday": "9:00-13:00"
            }),
            join_date=date(2020, 1, 1),
            is_active=True,
            teaching_responsibilities="Clinical Training Supervisor, Medical Student Mentor",
            administrative_roles="Department Head, Clinical Research Lead"
        )
        
        # Create Resident Doctor
        resident = Doctor(
            email="resident@medicai.com",
            hashed_password=get_password_hash("resident123"),
            first_name="Sarah",
            last_name="Johnson",
            medical_license_number="RES789012",
            qualifications="MD",
            specialty="Cardiology",
            subspecialty=None,
            years_of_experience=3,
            doctor_type="resident",
            date_of_birth=date(1990, 8, 25),
            gender="Female",
            contact_number="+1234567891",
            emergency_contact="+1987654322",
            department="Cardiology",
            office_location="Building A, Floor 3, Room 315",
            consultation_hours=json.dumps({
                "Monday": "8:00-16:00",
                "Tuesday": "8:00-16:00",
                "Thursday": "8:00-16:00"
            }),
            join_date=date(2022, 7, 1),
            is_active=True,
            graduation_date=date(2022, 6, 15),
            rotation_schedule=json.dumps({
                "Q1": "General Cardiology",
                "Q2": "Cardiac ICU",
                "Q3": "Cath Lab",
                "Q4": "Outpatient Clinic"
            })
        )
        
        # Add doctors to the database
        db.add(consultant)
        db.add(resident)
        db.commit()
        
        print("Successfully created test doctors!")
        print("\nConsultant Doctor:")
        print("Email: consultant@medicai.com")
        print("Password: consultant123")
        print("\nResident Doctor:")
        print("Email: resident@medicai.com")
        print("Password: resident123")
        
    except Exception as e:
        print(f"Error creating test doctors: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_doctors()
