from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.patient import Patient, ClinicalRecord
from app.models.patient_assignment import PatientAssignment
from app.schemas.patient import (
    PatientCreate, 
    PatientUpdate, 
    ClinicalRecordCreate,
    PatientAssignmentCreate
)

def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_patients_by_consultant(
    db: Session, 
    consultant_id: int,
    skip: int = 0, 
    limit: int = 100
) -> List[Patient]:
    return db.query(Patient)\
        .filter(Patient.consultant_id == consultant_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_patients_by_resident(
    db: Session, 
    resident_id: int,
    skip: int = 0, 
    limit: int = 100
) -> List[Patient]:
    return db.query(Patient)\
        .filter(Patient.current_resident_id == resident_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_patient(db: Session, patient: PatientCreate) -> Patient:
    db_patient = Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        consultant_id=patient.consultant_id,
        current_resident_id=patient.current_resident_id,
        risk_factors=patient.risk_factors,
        family_history=patient.family_history,
        surgical_history=patient.surgical_history,
        additional_notes=patient.additional_notes
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(
    db: Session, 
    db_patient: Patient,
    patient: PatientUpdate
) -> Patient:
    update_data = patient.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def assign_patient_to_resident(
    db: Session, 
    patient_id: int,
    resident_id: int
) -> Optional[Patient]:
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None

    # End current assignment if exists
    if db_patient.current_resident_id:
        current_assignment = db.query(PatientAssignment)\
            .filter(
                PatientAssignment.patient_id == patient_id,
                PatientAssignment.resident_id == db_patient.current_resident_id,
                PatientAssignment.ended_at.is_(None)
            ).first()
        if current_assignment:
            current_assignment.ended_at = datetime.utcnow()
            db.add(current_assignment)

    # Create new assignment
    new_assignment = PatientAssignment(
        patient_id=patient_id,
        resident_id=resident_id
    )
    db.add(new_assignment)

    # Update patient's current resident
    db_patient.current_resident_id = resident_id
    db.add(db_patient)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient

def create_clinical_record(
    db: Session, 
    record: ClinicalRecordCreate,
    created_by_id: int
) -> ClinicalRecord:
    db_record = ClinicalRecord(
        patient_id=record.patient_id,
        created_by_id=created_by_id,
        audio_file_path=record.audio_file_path,
        transcription=record.transcription,
        extracted_data=record.extracted_data,
        is_processed=False,
        processing_status="pending"
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_patient_clinical_records(
    db: Session, 
    patient_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[ClinicalRecord]:
    return db.query(ClinicalRecord)\
        .filter(ClinicalRecord.patient_id == patient_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_clinical_record(db: Session, record_id: int) -> Optional[ClinicalRecord]:
    return db.query(ClinicalRecord).filter(ClinicalRecord.id == record_id).first()

def get_patient_assignment_history(
    db: Session,
    patient_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[PatientAssignment]:
    return db.query(PatientAssignment)\
        .filter(PatientAssignment.patient_id == patient_id)\
        .order_by(PatientAssignment.assigned_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
