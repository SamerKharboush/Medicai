from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class PatientAssignment(Base):
    __tablename__ = "patient_assignments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    resident_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)  # Null means currently assigned

    # Relationships
    patient = relationship("Patient")
    resident = relationship("Doctor")
