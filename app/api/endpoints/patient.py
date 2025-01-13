from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models import Patient, ClinicalHistory
from app.core.auth import get_current_user
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    ClinicalHistoryResponse
)

router = APIRouter()

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new patient"""
    db_patient = Patient(
        medical_record_number=patient.medical_record_number,
        full_name=patient.full_name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of patients with optional search"""
    query = db.query(Patient)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            Patient.full_name.ilike(search) |
            Patient.medical_record_number.ilike(search)
        )
    
    patients = query.offset(skip).limit(limit).all()
    return patients

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get patient by ID"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update patient information"""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    for field, value in patient_update.dict(exclude_unset=True).items():
        setattr(db_patient, field, value)
    
    db_patient.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete patient"""
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(db_patient)
    db.commit()
    return {"message": "Patient deleted successfully"}

@router.get("/{patient_id}/history", response_model=List[ClinicalHistoryResponse])
async def get_patient_history(
    patient_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get patient's clinical history"""
    histories = db.query(ClinicalHistory)\
        .filter(ClinicalHistory.patient_id == patient_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return histories
