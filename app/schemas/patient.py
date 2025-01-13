from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from .doctor import Doctor

class PatientBase(BaseModel):
    name: str
    age: int
    gender: str
    risk_factors: Dict[str, bool] = {}
    family_history: List[str] = []
    surgical_history: List[str] = []
    additional_notes: List[str] = []

class PatientCreate(PatientBase):
    consultant_id: int
    current_resident_id: Optional[int] = None

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    risk_factors: Optional[Dict[str, bool]] = None
    family_history: Optional[List[str]] = None
    surgical_history: Optional[List[str]] = None
    additional_notes: Optional[List[str]] = None
    current_resident_id: Optional[int] = None

class ClinicalRecordBase(BaseModel):
    transcription: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None

class ClinicalRecordCreate(ClinicalRecordBase):
    patient_id: int
    audio_file_path: str

class ClinicalRecordUpdate(ClinicalRecordBase):
    is_processed: Optional[bool] = None
    processing_status: Optional[str] = None

class ClinicalRecordInDB(ClinicalRecordBase):
    id: int
    patient_id: int
    created_by_id: int
    recorded_at: datetime
    is_processed: bool
    processing_status: Optional[str]
    created_by: Doctor

    class Config:
        from_attributes = True

class PatientInDB(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    consultant: Doctor
    current_resident: Optional[Doctor]
    clinical_records: List[ClinicalRecordInDB] = []

    class Config:
        from_attributes = True

class Patient(PatientInDB):
    pass

# Schema for Patient Assignment
class PatientAssignmentBase(BaseModel):
    patient_id: int
    resident_id: int

class PatientAssignmentCreate(PatientAssignmentBase):
    pass

class PatientAssignmentUpdate(BaseModel):
    ended_at: datetime

class PatientAssignmentInDB(PatientAssignmentBase):
    id: int
    assigned_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True
