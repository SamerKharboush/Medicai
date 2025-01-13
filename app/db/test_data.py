from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.models.doctor import Doctor, DoctorType
from app.models.patient import Patient, ClinicalRecord
from app.core.security import get_password_hash

def create_test_data(db: Session) -> None:
    # Create Consultant Doctor Account
    consultant = Doctor(
        email="dr.williams@medicai.com",
        hashed_password=get_password_hash("DrWilliams2024!"),  # Password meets complexity requirements
        first_name="Robert",
        last_name="Williams",
        medical_license_number="CON123456",
        qualifications="MD, PhD, FRCS",
        specialty="Cardiology",
        subspecialty="Interventional Cardiology",
        years_of_experience=15,
        doctor_type="consultant",
        date_of_birth=date(1975, 5, 15),
        gender="male",
        contact_number="+1234567890",
        emergency_contact="+1234567891",
        department="Cardiology",
        office_location="Building A, Room 101",
        consultation_hours='{"Monday": "9:00-17:00", "Wednesday": "9:00-17:00", "Friday": "9:00-13:00"}',
        join_date=date(2010, 1, 1),
        is_active=True,
        bio="""Dr. Robert Williams is a distinguished cardiologist with over 15 years of experience in interventional cardiology. 
        He specializes in complex coronary interventions and structural heart disease.""",
        research_interests="""- Innovative approaches in interventional cardiology
        - Advanced cardiac imaging techniques
        - Novel therapeutic strategies in heart failure""",
        publications="""1. "Novel Approaches in Interventional Cardiology" - Cardiology Journal 2023
        2. "Long-term Outcomes of Complex Coronary Interventions" - Heart 2022
        3. "Advanced Imaging in Structural Heart Disease" - JACC 2021""",
        certifications="""- Board Certified in Cardiovascular Disease
        - Fellow of the American College of Cardiology
        - Advanced Cardiac Life Support Instructor
        - Certified in Structural Heart Interventions""",
        teaching_responsibilities="""- Clinical Director of Cardiology Fellowship Program
        - Supervisor for cardiology residents
        - Weekly cardiac catheterization conference leader""",
        administrative_roles="""- Head of Cardiology Department
        - Member of Hospital Medical Board
        - Chair of Quality Improvement Committee"""
    )
    db.add(consultant)
    db.flush()  # This will assign an ID to the consultant

    # Create Resident Doctor Account
    resident = Doctor(
        email="dr.chen@medicai.com",
        hashed_password=get_password_hash("DrChen2024!"),  # Password meets complexity requirements
        first_name="Sarah",
        last_name="Chen",
        medical_license_number="RES789012",
        qualifications="MD",
        specialty="Cardiology",
        subspecialty="General Cardiology",
        years_of_experience=2,
        doctor_type="resident",
        date_of_birth=date(1992, 8, 22),
        gender="female",
        contact_number="+0987654321",
        emergency_contact="+0987654322",
        department="Cardiology",
        office_location="Building B, Room 203",
        consultation_hours='{"Tuesday": "9:00-17:00", "Thursday": "9:00-17:00"}',
        join_date=date(2022, 7, 1),
        is_active=True,
        bio="""Dr. Sarah Chen is a dedicated second-year cardiology resident with a strong interest in non-invasive cardiac imaging 
        and preventive cardiology. She completed her medical degree with honors and is passionate about patient-centered care.""",
        research_interests="""- Non-invasive cardiac imaging
        - Preventive cardiology
        - Women's cardiovascular health
        - Digital health in cardiology""",
        publications="""1. "Case Report: Novel Findings in Stress Echocardiography" - Cardiology Cases 2023
        2. "Review: Digital Health Applications in Preventive Cardiology" - Digital Health Journal 2023""",
        certifications="""- Basic Life Support (BLS)
        - Advanced Cardiac Life Support (ACLS)
        - Nuclear Cardiology Board Eligible
        - Level 1 Echo Certification""",
        supervisor_id=consultant.id,  # Assign Dr. Williams as supervisor
        graduation_date=date(2025, 6, 30),
        rotation_schedule='''{
            "current": {
                "rotation": "Cardiac Catheterization Lab",
                "duration": "3 months",
                "supervisor": "Dr. Robert Williams"
            },
            "next": {
                "rotation": "Echo Lab",
                "duration": "3 months",
                "supervisor": "Dr. Emily Taylor"
            },
            "schedule": {
                "Monday": "Cath Lab Procedures",
                "Tuesday": "Outpatient Clinic",
                "Wednesday": "Research/Academic Time",
                "Thursday": "Outpatient Clinic",
                "Friday": "Conferences/Grand Rounds"
            }
        }'''
    )
    db.add(resident)

    # Create test patients
    test_patients = [
        {
            "name": "Alice Johnson",
            "age": 33,  # Calculated from date of birth
            "gender": "female",
            "risk_factors": {
                "hypertension": True,
                "diabetes": True,
                "cad_family_history": True
            },
            "family_history": [
                "Father: Coronary Artery Disease",
                "Mother: Hypertension"
            ],
            "surgical_history": [
                "Appendectomy (2015)"
            ],
            "consultant_id": consultant.id,
            "current_resident_id": resident.id
        },
        {
            "name": "Bob Wilson",
            "age": 38,  # Calculated from date of birth
            "gender": "male",
            "risk_factors": {
                "cad": True,
                "previous_mi": True,
                "hypertension": True,
                "hyperlipidemia": True
            },
            "family_history": [
                "Mother: Type 2 Diabetes",
                "Father: Myocardial Infarction at age 55"
            ],
            "surgical_history": [
                "PCI with stent placement (2021)"
            ],
            "consultant_id": consultant.id,
            "current_resident_id": resident.id
        }
    ]

    for patient_data in test_patients:
        patient = Patient(**patient_data)
        db.add(patient)

    try:
        db.commit()
    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
        raise

test_doctors = [
    {
        "email": "test.doctor@medicai.com",
        "hashed_password": get_password_hash("Test123!@#"),
        "first_name": "Test",
        "last_name": "Doctor",
        "medical_license_number": "ML123456",
        "qualifications": "MD",
        "specialty": "General Practice",
        "years_of_experience": 5,
        "doctor_type": DoctorType.RESIDENT,
        "date_of_birth": datetime.now() - timedelta(days=365*30),
        "gender": "Male",
        "contact_number": "+1234567890",
        "department": "Emergency",
        "office_location": "Room 101, Building A",
        "graduation_date": datetime.now() - timedelta(days=365*2),
        "join_date": datetime.now() - timedelta(days=365*2),
        "is_active": True
    },
    {
        "email": "dr.williams@medicai.com",
        "hashed_password": get_password_hash("DrWilliams2024!"),
        "first_name": "John",
        "last_name": "Williams",
        "medical_license_number": "ML789012",
        "qualifications": "MD, PhD",
        "specialty": "Cardiology",
        "years_of_experience": 15,
        "doctor_type": DoctorType.CONSULTANT,
        "date_of_birth": datetime.now() - timedelta(days=365*45),
        "gender": "Male",
        "contact_number": "+1987654321",
        "department": "Cardiology",
        "office_location": "Room 305, Building B",
        "graduation_date": datetime.now() - timedelta(days=365*15),
        "join_date": datetime.now() - timedelta(days=365*10),
        "is_active": True
    }
]

def create_test_data(db):
    # Create test doctors
    for doctor_data in test_doctors:
        doctor = db.query(Doctor).filter(Doctor.email == doctor_data["email"]).first()
        if not doctor:
            doctor = Doctor(**doctor_data)
            db.add(doctor)
    
    db.commit()
