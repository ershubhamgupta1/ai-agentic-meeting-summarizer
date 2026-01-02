"""Lazy loading factory for ML models to improve startup performance."""

import logging

import whisper
from pyannote.audio import Inference, Pipeline

from config.settings import settings
from utils.exceptions import ModelLoadingError

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory for lazy-loading ML models."""

    _pipeline: Pipeline | None = None
    _whisper_model: whisper.Whisper | None = None
    _embedding_model: Inference | None = None

    @classmethod
    def get_pipeline(cls) -> Pipeline:
        """Get or create the speaker diarization pipeline."""
        if cls._pipeline is None:
            try:
                logger.info("Loading speaker diarization pipeline...")
                cls._pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1"
                )
                logger.info("Speaker diarization pipeline loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load diarization pipeline: {e}")
                raise ModelLoadingError(
                    f"Failed to load speaker diarization pipeline: {e}"
                ) from e
        return cls._pipeline

    @classmethod
    def get_whisper_model(cls) -> whisper.Whisper:
        """Get or create the Whisper transcription model."""
        if cls._whisper_model is None:
            try:
                logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}...")
                cls._whisper_model = whisper.load_model(settings.WHISPER_MODEL)
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise ModelLoadingError(f"Failed to load Whisper model: {e}") from e
        return cls._whisper_model

    @classmethod
    def get_embedding_model(cls) -> Inference:
        """Get or create the speaker embedding model."""
        if cls._embedding_model is None:
            try:
                logger.info("Loading speaker embedding model...")
                # Token is handled via environment variable in hf_compat.py
                cls._embedding_model = Inference("pyannote/embedding", window="whole")
                logger.info("Speaker embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise ModelLoadingError(
                    f"Failed to load speaker embedding model: {e}"
                ) from e
        return cls._embedding_model

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached models (useful for testing or memory management)."""
        cls._pipeline = None
        cls._whisper_model = None
        cls._embedding_model = None
        logger.info("Model cache cleared")
