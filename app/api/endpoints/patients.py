from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_doctor
from app.crud import patient as crud_patient
from app.models.doctor import Doctor, DoctorType
from app.schemas.patient import (
    Patient,
    PatientCreate,
    PatientUpdate,
    ClinicalRecordCreate,
    ClinicalRecordInDB,
    PatientAssignmentInDB
)
from app.services.audio_processing import process_audio_file
from app.services.nlp_processing import extract_medical_data

router = APIRouter()

@router.post("/", response_model=Patient)
def create_patient(
    *,
    db: Session = Depends(get_db),
    patient_in: PatientCreate,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Patient:
    """
    Create new patient.
    Only consultants can create new patients.
    """
    if current_doctor.doctor_type != DoctorType.CONSULTANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can create new patients"
        )
    return crud_patient.create_patient(db=db, patient=patient_in)

@router.get("/my-patients", response_model=List[Patient])
def read_my_patients(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> List[Patient]:
    """
    Retrieve patients assigned to the current doctor.
    """
    if current_doctor.doctor_type == DoctorType.CONSULTANT:
        patients = crud_patient.get_patients_by_consultant(
            db, consultant_id=current_doctor.id, skip=skip, limit=limit
        )
    else:  # RESIDENT
        patients = crud_patient.get_patients_by_resident(
            db, resident_id=current_doctor.id, skip=skip, limit=limit
        )
    return patients

@router.get("/{patient_id}", response_model=Patient)
def read_patient(
    *,
    db: Session = Depends(get_db),
    patient_id: int,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Patient:
    """
    Get patient by ID.
    Doctors can only access their assigned patients.
    """
    patient = crud_patient.get_patient(db=db, patient_id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if doctor has access to this patient
    if current_doctor.doctor_type == DoctorType.CONSULTANT:
        if patient.consultant_id != current_doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this patient"
            )
    else:  # RESIDENT
        if patient.current_resident_id != current_doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this patient"
            )
    
    return patient

@router.put("/{patient_id}", response_model=Patient)
def update_patient(
    *,
    db: Session = Depends(get_db),
    patient_id: int,
    patient_in: PatientUpdate,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Patient:
    """
    Update a patient.
    Doctors can only update their assigned patients.
    """
    patient = crud_patient.get_patient(db=db, patient_id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if doctor has access to this patient
    if current_doctor.doctor_type == DoctorType.CONSULTANT:
        if patient.consultant_id != current_doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this patient"
            )
    else:  # RESIDENT
        if patient.current_resident_id != current_doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this patient"
            )
    
    return crud_patient.update_patient(db=db, db_patient=patient, patient=patient_in)

@router.post("/{patient_id}/assign", response_model=Patient)
def assign_patient(
    *,
    db: Session = Depends(get_db),
    patient_id: int,
    resident_id: int,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> Patient:
    """
    Assign a patient to a resident.
    Only consultants can assign patients.
    """
    if current_doctor.doctor_type != DoctorType.CONSULTANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consultants can assign patients"
        )
    
    patient = crud_patient.get_patient(db=db, patient_id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if patient.consultant_id != current_doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to assign this patient"
        )
    
    return crud_patient.assign_patient_to_resident(
        db=db, patient_id=patient_id, resident_id=resident_id
    )

@router.get("/{patient_id}/assignments", response_model=List[PatientAssignmentInDB])
def read_patient_assignments(
    *,
    db: Session = Depends(get_db),
    patient_id: int,
    skip: int = 0,
    limit: int = 100,
    current_doctor: Doctor = Depends(get_current_doctor)
) -> List[PatientAssignmentInDB]:
    """
    Get patient assignment history.
    Only the consultant and current resident can view assignments.
    """
    patient = crud_patient.get_patient(db=db, patient_id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if (current_doctor.doctor_type == DoctorType.CONSULTANT and 
        patient.consultant_id != current_doctor.id) or \
       (current_doctor.doctor_type == DoctorType.RESIDENT and 
        patient.current_resident_id != current_doctor.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this patient's assignments"
        )
    
    return crud_patient.get_patient_assignment_history(
        db=db, patient_id=patient_id, skip=skip, limit=limit
    )

@router.post("/{patient_id}/clinical-records", response_model=ClinicalRecordInDB)
async def create_clinical_record(
    *,
    db: Session = Depends(get_db),
    patient_id: int,
    audio_file: UploadFile = File(...),
    current_doctor: Doctor = Depends(get_current_doctor)
) -> ClinicalRecordInDB:
    """
    Create a new clinical record from audio file.
    Only the current resident can create records.
    """
    patient = crud_patient.get_patient(db=db, patient_id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if current_doctor.doctor_type != DoctorType.RESIDENT or \
       patient.current_resident_id != current_doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned resident can create clinical records"
        )
    
    # Process audio file
    audio_path, transcription = await process_audio_file(audio_file)
    
    # Extract medical data using NLP
    extracted_data = await extract_medical_data(transcription)
    
    record_in = ClinicalRecordCreate(
        patient_id=patient_id,
        audio_file_path=audio_path,
        transcription=transcription,
        extracted_data=extracted_data
    )
    
    return crud_patient.create_clinical_record(
        db=db, record=record_in, created_by_id=current_doctor.id
    )
