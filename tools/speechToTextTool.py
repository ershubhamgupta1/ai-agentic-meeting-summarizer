import logging
import os
from typing import Any

from dotenv import load_dotenv

from utils.exceptions import TranscriptionError
from utils.model_factory import ModelFactory

load_dotenv()  # Load environment variables from .env

logger = logging.getLogger(__name__)


def speechToTextTool(mp3File: str) -> dict[str, Any]:
    """
    Convert audio file to text using Whisper transcription.

    Args:
        mp3File: Path to the audio file to transcribe

    Returns:
        Dictionary with success status, transcribed text, language, and duration

    Raises:
        TranscriptionError: If transcription fails
    """
    try:
        if not os.path.exists(mp3File):
            raise FileNotFoundError(f"Audio file not found: {mp3File}")

        logger.info(f"Transcribing audio file: {mp3File}")
        model = ModelFactory.get_whisper_model()
        transcript = model.transcribe(mp3File)

        logger.info(
            f"Transcription completed. Language: {transcript.get('language', 'unknown')}"
        )
        return {
            "success": True,
            "text": transcript["text"],
            "language": transcript.get("language", "unknown"),
            "duration": transcript.get("duration", 0),
        }
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        raise TranscriptionError(f"Audio file not found: {mp3File}") from e
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise TranscriptionError(f"Transcription failed: {e}") from e
