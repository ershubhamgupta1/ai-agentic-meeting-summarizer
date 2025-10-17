# Create config/settings.py
import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class Settings:
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

    # Whisper Settings
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")

    # App Settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB
    SUPPORTED_FORMATS: list = [".mp3", ".wav", ".m4a"]

    # UI Settings
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "false").lower() == "true"


# Add to config/settings.py
def validate_environment() -> bool:
    """Validate required environment variables."""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    return True


settings = Settings()
