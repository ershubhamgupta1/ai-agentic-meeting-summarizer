# Add to utils/file_utils.py
import logging
import os

from config.settings import settings

logger = logging.getLogger(__name__)


def validate_audio_file(file_path: str) -> bool:
    """Validate audio file before processing."""
    if not os.path.exists(file_path):
        return False

    if os.path.getsize(file_path) > settings.MAX_FILE_SIZE:
        return False

    _, ext = os.path.splitext(file_path)
    return ext.lower() in settings.SUPPORTED_FORMATS


def cleanup_temp_file(file_path: str) -> None:
    """Safely remove temporary files."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {e}")
