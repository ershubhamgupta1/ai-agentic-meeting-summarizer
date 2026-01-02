# Add to utils/file_utils.py
import logging
import os
import subprocess
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


def ensure_wav_16k_mono(audio_path: str) -> str:
    audio_path = Path(audio_path)

    if audio_path.suffix.lower() == ".wav":
        return str(audio_path)

    wav_path = audio_path.with_suffix(".wav")

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(audio_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-acodec",
        "pcm_s16le",
        str(wav_path),
    ]

    subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    return str(wav_path)
