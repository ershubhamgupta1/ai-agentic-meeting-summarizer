# Add to utils/file_utils.py
import logging
import os
from pathlib import Path

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


def read_folder(folder_path: Path) -> list[Path]:
    """Read a folder and return all files inside it."""
    if not folder_path.exists():
        logger.error(f"Folder does not exist: {folder_path}")
        return []

    files = [f for f in folder_path.iterdir() if f.is_file()]
    logger.info(f"Found {len(files)} files in {folder_path}")
    return files


def load_file(file_path: Path) -> str:
    """Load a single file."""
    logger.info(f"Loading file: {file_path.name}")

    with open(file_path, encoding="utf-8") as f:
        return f.read()
