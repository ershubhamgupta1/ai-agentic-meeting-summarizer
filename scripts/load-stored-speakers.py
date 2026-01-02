from utils.hf_compat import patch_hf_hub_download

# ruff: noqa: E402
patch_hf_hub_download()  # 🔥 MUST be before pyannote imports
import asyncio
import json
import logging
from pathlib import Path

from tools import addSpeakerInStoreTool
from utils.file_utils import load_file

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "stored-speakers"
SPEAKER_DATA_FILE = "speakers-data.json"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def LoadSpeakers():
    speakersData = load_file(DATA_DIR / SPEAKER_DATA_FILE)
    speakersData = json.loads(speakersData)

    for speaker in speakersData["data"]:
        speakerFiles = speaker["fileNames"]
        for speakerFile in speakerFiles:
            audio_path = DATA_DIR / speakerFile
            await addSpeakerInStoreTool(audio_path, speaker["speakerName"])


async def main() -> None:
    # ()
    await LoadSpeakers()


if __name__ == "__main__":
    asyncio.run(main())
