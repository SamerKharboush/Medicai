import os
import whisper
from pathlib import Path
from typing import Optional
import torch

class SpeechToTextService:
    def __init__(self):
        # Determine the device to use
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Set Whisper models directory from environment variable
        models_dir = os.getenv("WHISPER_MODELS_DIR", str(Path.home() / ".cache" / "whisper"))
        os.makedirs(models_dir, exist_ok=True)
        os.environ["XDG_CACHE_HOME"] = models_dir
        
        # Load Whisper model (can be 'tiny', 'base', 'small', 'medium', 'large')
        self.model = whisper.load_model("base").to(self.device)
        
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribe an audio file to text using OpenAI's Whisper model.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            # Check if file exists
            if not Path(audio_path).exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Transcribe audio
            result = self.model.transcribe(audio_path)
            return result["text"]
            
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return None
    
    def transcribe_audio_with_timestamps(self, audio_path: str) -> Optional[dict]:
        """
        Transcribe an audio file and return text with timestamps.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing segments with text and timestamps
        """
        try:
            # Check if file exists
            if not Path(audio_path).exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Transcribe audio with word-level timestamps
            result = self.model.transcribe(audio_path, word_timestamps=True)
            return result
            
        except Exception as e:
            print(f"Error transcribing audio with timestamps: {str(e)}")
            return None

# Create a singleton instance
speech_to_text_service = SpeechToTextService()
