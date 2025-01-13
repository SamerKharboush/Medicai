from sqlalchemy import Column, String, Date, Enum, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import date

class DoctorType(str, enum.Enum):
    CONSULTANT = "consultant"
    RESIDENT = "resident"

class Specialty(str, enum.Enum):
    GENERAL_PRACTICE = "General Practice"
    CARDIOLOGY = "Cardiology"
    NEUROLOGY = "Neurology"
    PEDIATRICS = "Pediatrics"
    ORTHOPEDICS = "Orthopedics"
    PSYCHIATRY = "Psychiatry"
    DERMATOLOGY = "Dermatology"
    ONCOLOGY = "Oncology"
    EMERGENCY_MEDICINE = "Emergency Medicine"
    INTERNAL_MEDICINE = "Internal Medicine"

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    
    # Professional Information
    medical_license_number = Column(String(50), unique=True, nullable=False)
    qualifications = Column(String(200), nullable=False)  # e.g., "MD, PhD, FRCS"
    specialty = Column(String(50), nullable=False)
    subspecialty = Column(String(100))  # Optional subspecialty
    years_of_experience = Column(Integer, nullable=False)
    doctor_type = Column(String(20), nullable=False)
    
    # Additional Information
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    contact_number = Column(String(20), nullable=False)
    emergency_contact = Column(String(20))
    
    # Work Details
    department = Column(String(100), nullable=False)
    office_location = Column(String(100))
    consultation_hours = Column(String(200))  # JSON string of consultation hours
    join_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Professional Profile
    bio = Column(Text)  # Brief professional biography
    research_interests = Column(Text)  # For academic/research interests
    publications = Column(Text)  # List of publications (can be JSON string)
    certifications = Column(Text)  # List of certifications (can be JSON string)
    
    # For residents only
    supervisor_id = Column(Integer, ForeignKey('doctors.id'), nullable=True)
    graduation_date = Column(Date, nullable=True)  # Expected graduation date for residents
    rotation_schedule = Column(Text)  # Current rotation schedule (can be JSON string)
    
    # For consultants only
    teaching_responsibilities = Column(Text)  # Description of teaching duties
    administrative_roles = Column(Text)  # Administrative positions held
    
    # Relationships
    supervisor = relationship(
        "Doctor",
        remote_side=[id],
        backref="supervised_residents",
        foreign_keys=[supervisor_id]
    )
    
    # Patient relationships
    supervised_patients = relationship(
        "Patient",
        primaryjoin="Doctor.id == Patient.consultant_id",
        overlaps="supervised_residents",
        lazy="dynamic"
    )
    
    assigned_patients = relationship(
        "Patient",
        primaryjoin="Doctor.id == Patient.current_resident_id",
        overlaps="supervised_residents",
        lazy="dynamic"
    )
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_consultant(self):
        return self.doctor_type == DoctorType.CONSULTANT
    
    @property
    def is_resident(self):
        return self.doctor_type == DoctorType.RESIDENT
