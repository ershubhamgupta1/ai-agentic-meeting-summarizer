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
    PORT: int = int(os.getenv("PORT", "7860"))
    _running_in_space_env = os.getenv("RUNNING_IN_SPACE", "")
    RUNNING_IN_SPACE: bool = _running_in_space_env.lower() not in {
        "",
        "0",
        "false",
        "no",
    }
    _gradio_share_env = os.getenv("GRADIO_SHARE")
    GRADIO_SHARE: bool = (
        _gradio_share_env.lower() == "true"
        if _gradio_share_env is not None
        else not RUNNING_IN_SPACE
    )


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
logger.info(
    "Settings loaded (RUNNING_IN_SPACE=%s, GRADIO_SHARE=%s, PORT=%s)",
    settings.RUNNING_IN_SPACE,
    settings.GRADIO_SHARE,
    settings.PORT,
)
