import os

os.environ["PYANNOTE_AUDIO_DISABLE_TORCHCODEC"] = "1"

import logging
import tempfile
from collections.abc import AsyncGenerator

import torchaudio

# Enhanced main.py with proper typing
from tools import (
    speakerIdentificationTool,
    speechToTextTool,
    summaryTool,
    textRefiningTool,
)
from utils.exceptions import TranscriptionError
from utils.getMarkdown import generate_markdown_summary

logger = logging.getLogger(__name__)


async def summaryAgent(
    input_path: str,
) -> AsyncGenerator[tuple[str, str | None], None]:
    """
    Process audio file through transcription and summarization pipeline.

    Args:
        input_path: Path to the audio file to process

    Yields:
        Tuple of (status_message, accumulated_markdown_summary)
    """
    try:
        yield "🧠 Transcription started...", None

        # 1) Transcribe audio
        logger.info(f"Transcribing audio file: {input_path}")
        try:
            transcript_result = speechToTextTool(input_path)
        except TranscriptionError as e:
            yield (f"❌ Transcription failed: {str(e)}", None)
            return

        if not transcript_result.get("success", False):
            yield (
                f"❌ Transcription failed: {transcript_result.get('error', 'Unknown error')}",
                None,
            )
            return

        yield "✅ Transcription completed.", None

        # 2) Identify speakers from the original audio
        yield "🗣️ Identifying speakers from the meeting audio...", None
        speakers: list[str] = []
        speaker_result = speakerIdentificationTool(input_path)

        if speaker_result.get("success"):
            speakers = speaker_result.get("identified_speakers", []) or []
            logger.info(f"Identified speakers: {speakers}")

            if speakers:
                yield (
                    "✅ Speaker identification completed: "
                    + ", ".join(sorted(speakers)),
                    None,
                )
            else:
                yield "⚠️ No known speakers identified in the audio.", None
        else:
            error_msg = speaker_result.get(
                "error", "Unknown speaker identification error"
            )
            logger.warning(f"Speaker identification did not succeed: {error_msg}")
            yield f"⚠️ Speaker identification issue: {error_msg}", None

        # 3) Refine transcript
        logger.info("Summarizing transcript...")
        yield "🧠 Refining transcript...", None

        refined_transcript = textRefiningTool(transcript_result["text"])
        yield "✅ Refinement completed.", None

        logger.info(
            f"original transcript word count: {len(transcript_result['text'].split())}"
        )
        logger.info(f"Refined transcript word count: {len(refined_transcript.split())}")

        logger.info(f"original transcript word : {transcript_result['text']}")
        logger.info(f"Refined transcript word : {refined_transcript}")

        # 4) Call summarization agent
        summary = summaryTool(refined_transcript)
        yield "✅ Summary generation completed.", None

        # 5) Generate markdown from structured summary
        marked_down_data = generate_markdown_summary(summary)

        # 6) Enrich markdown with detected speakers (if any)
        if speakers:
            detected_speakers_md = "\n".join(f"- `{spk}`" for spk in sorted(speakers))
            speakers_section = f"## 🗣️ Detected Speakers\n{detected_speakers_md}\n\n"

            # Inject the speakers section just after the main title if present
            if "# 📋 Meeting Summary" in marked_down_data:
                marked_down_data = marked_down_data.replace(
                    "# 📋 Meeting Summary",
                    "# 📋 Meeting Summary\n\n" + speakers_section,
                    1,
                )
            else:
                # Fallback: prepend the section at the top
                marked_down_data = speakers_section + marked_down_data

        yield "✅ Summary complete.", marked_down_data

    except Exception as e:
        logger.error(f"Error in summaryAgent: {e}")
        yield f"❌ Error: {str(e)}", None


async def voiceRecognitionAgent(input_path: str) -> dict:
    """
    Identify speakers in an audio file.

    Args:
        input_path: Path to the audio file to analyze

    Returns:
        Dictionary with success status, identified speakers, and events
    """
    return speakerIdentificationTool(input_path)


def save_segment(audio, sr, start, end):
    """
    Save an audio segment to a temporary WAV file.

    Args:
        audio: Audio tensor
        sr: Sample rate
        start: Start time in seconds
        end: End time in seconds

    Returns:
        Path to the temporary WAV file
    """
    start, end = int(start * sr), int(end * sr)
    segment = audio[:, start:end]

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        torchaudio.save(tmp.name, segment, sr)
        return tmp.name
