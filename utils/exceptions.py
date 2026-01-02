"""Custom exceptions for the meeting summarizer application."""


class TranscriptionError(Exception):
    """Raised when audio transcription fails."""

    pass


class SpeakerIdentificationError(Exception):
    """Raised when speaker identification fails."""

    pass


class SummarizationError(Exception):
    """Raised when summarization fails."""

    pass


class AudioProcessingError(Exception):
    """Raised when audio processing fails."""

    pass


class ModelLoadingError(Exception):
    """Raised when model loading fails."""

    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""

    pass
