from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
from datetime import datetime

from app.db.session import get_db
from app.services.speech_to_text import speech_to_text_service
from app.services.medical_nlp import medical_nlp_service
from app.crud import patient as crud_patient
from app.schemas.patient import (
    ClinicalHistoryCreate,
    ClinicalHistoryResponse,
    ClinicalHistoryUpdate
)

router = APIRouter()

@router.post("/upload/{patient_id}", response_model=ClinicalHistoryResponse)
async def upload_clinical_history(
    patient_id: int,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a clinical history audio recording
    """
    # Check if patient exists
    db_patient = crud_patient.get_patient(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Create directory for audio files if it doesn't exist
    audio_dir = "uploads/audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    # Save audio file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"{patient_id}_{timestamp}_{audio_file.filename}"
    audio_path = os.path.join(audio_dir, audio_filename)
    
    with open(audio_path, "wb") as buffer:
        content = await audio_file.read()
        buffer.write(content)
    
    # Transcribe audio
    transcription = speech_to_text_service.transcribe_audio(audio_path)
    if not transcription:
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")
    
    # Process transcription with NLP
    extracted_data = await medical_nlp_service.process_medical_text(transcription)
    
    # Create clinical history record
    clinical_history = ClinicalHistoryCreate(
        patient_id=patient_id,
        original_audio_path=audio_path,
        transcribed_text=transcription,
        age=extracted_data["demographics"]["age"],
        risk_factors=extracted_data["risk_factors"],
        family_history=extracted_data["family_history"],
        surgical_history=extracted_data["surgical_history"]
    )
    
    db_record = crud_patient.create_clinical_record(db, clinical_history)
    return db_record

@router.get("/patient/{patient_id}", response_model=List[ClinicalHistoryResponse])
def get_patient_history(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all clinical history records for a patient
    """
    # Check if patient exists
    if not crud_patient.get_patient(db, patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return crud_patient.get_patient_clinical_records(db, patient_id)

@router.get("/{record_id}", response_model=ClinicalHistoryResponse)
def get_clinical_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific clinical history record
    """
    db_record = crud_patient.get_clinical_record(db, record_id)
    if not db_record:
        raise HTTPException(status_code=404, detail="Clinical record not found")
    return db_record
