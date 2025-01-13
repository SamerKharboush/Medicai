from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    medical_record_number = Column(String, unique=True, index=True)
    full_name = Column(String)
    date_of_birth = Column(DateTime)
    gender = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    clinical_histories = relationship("ClinicalHistory", back_populates="patient")

class ClinicalHistory(Base):
    __tablename__ = "clinical_histories"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    recorded_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Structured data
    age = Column(Integer)
    risk_factors = Column(JSON)  # Store as JSON array
    family_history = Column(JSON)  # Store as JSON array
    surgical_history = Column(JSON)  # Store as JSON array
    
    # Raw data
    original_audio_path = Column(String)
    transcribed_text = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    patient = relationship("Patient", back_populates="clinical_histories")
    recorded_by = relationship("User")
