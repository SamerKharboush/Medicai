from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Doctor Relationships
    consultant_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    current_resident_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    
    # Risk Factors
    risk_factors = Column(JSON, default=dict)  # Store as JSON: {"DM": true, "HTN": false, etc.}
    
    # Histories
    family_history = Column(JSON, default=list)  # Store as JSON array
    surgical_history = Column(JSON, default=list)  # Store as JSON array
    
    # Additional Data
    additional_notes = Column(JSON, default=list)  # Store as JSON array
    
    # Relationships
    clinical_records = relationship("ClinicalRecord", back_populates="patient")

class ClinicalRecord(Base):
    __tablename__ = "clinical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Doctor who created the record
    created_by_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    
    # Original Data
    audio_file_path = Column(String)  # Path to stored audio file
    transcription = Column(String)  # Full transcription text
    
    # Extracted Data
    extracted_data = Column(JSON)  # Store all extracted information as JSON
    
    # Metadata
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String)  # For tracking NLP processing status
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="clinical_records")
    created_by = relationship("Doctor", foreign_keys=[created_by_id])