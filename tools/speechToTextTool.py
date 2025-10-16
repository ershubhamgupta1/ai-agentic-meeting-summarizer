from dotenv import load_dotenv
import logging
from typing import Dict, Any
import os
import whisper

from config.settings import settings

load_dotenv()  # Load environment variables from .env

# Add to top of speechToTextTool.py
_model_cache = {}
logger = logging.getLogger(__name__)

def speechToTextTool(mp3File: str) -> Dict[str, Any]:
    """Tool to convert mp3 file to text with comprehensive error handling."""
    try:
        if not os.path.exists(mp3File):
            raise FileNotFoundError(f"Audio file not found: {mp3File}")
        
        if settings.WHISPER_MODEL not in _model_cache:
            logger.info("Loading Whisper model...")
            _model_cache[settings.WHISPER_MODEL] = whisper.load_model(settings.WHISPER_MODEL)
        
        logger.info(f"model loaded!!!!!!!!!")
        model = _model_cache[settings.WHISPER_MODEL]
        transcript = model.transcribe(mp3File)
        logger.info(f"transcript: {transcript['text']}")
        return {
            "success": True,
            "text": transcript["text"],
            "language": transcript.get("language", "unknown"),
            "duration": transcript.get("duration", 0)
        }
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return {"success": False, "error": "Transcription failed"}