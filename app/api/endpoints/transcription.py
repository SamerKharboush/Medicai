from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import tempfile
from pathlib import Path

from app.db.database import get_db
from app.services.transcription import transcription_service
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/process-audio")
async def process_audio(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process audio file and extract medical information
    """
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an audio file"
        )
    
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        content = await audio_file.read()
        temp_file.write(content)
        temp_file_path = Path(temp_file.name)
    
    try:
        # Transcribe audio
        transcription_result = await transcription_service.transcribe_audio(temp_file_path)
        
        if transcription_result["status"] == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcription_result['error']}"
            )
        
        # Extract medical information
        medical_info = await transcription_service.extract_medical_info(
            transcription_result["text"]
        )
        
        return {
            "transcription": transcription_result["text"],
            "medical_info": medical_info
        }
        
    finally:
        # Clean up temporary file
        temp_file_path.unlink()

@router.post("/save-clinical-history")
async def save_clinical_history(
    clinical_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Save processed clinical history to database
    """
    # TODO: Implement database storage
    return {"status": "success", "message": "Clinical history saved"}
