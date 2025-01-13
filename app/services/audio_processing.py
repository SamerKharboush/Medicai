import os
import whisper
from fastapi import UploadFile
from pathlib import Path
from datetime import datetime

# Initialize the Whisper model lazily
_model = None

def get_model():
    global _model
    if _model is None:
        # Use environment variable for model size or default to "base"
        model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        _model = whisper.load_model(model_size, download_root="/app/models")
    return _model

async def process_audio_file(audio_file: UploadFile) -> tuple[str, str]:
    """
    Process an audio file using Whisper for transcription.
    Returns the path where the audio is saved and the transcription.
    """
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{audio_file.filename}"
    file_path = uploads_dir / filename
    
    # Save uploaded file
    with open(file_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)
    
    # Get model and transcribe audio
    model = get_model()
    result = model.transcribe(str(file_path))
    transcription = result["text"]
    
    return str(file_path), transcription
