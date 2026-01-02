import logging
import pickle
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from pydub import AudioSegment
from sklearn.metrics.pairwise import cosine_similarity

from utils.exceptions import AudioProcessingError
from utils.file_utils import ensure_wav_16k_mono
from utils.model_factory import ModelFactory

# =========================
# CONFIGURATION
# =========================
logger = logging.getLogger(__name__)
SPEAKER_STORE_PATH = Path("speaker_store.pkl")

# Similarity threshold for speaker identification (tune as needed)
SIMILARITY_THRESHOLD = 0.60

# Minimum chunk length (ms) for reliable speaker identification
MIN_CHUNK_MS = 3000

# Minimum audio duration (ms) for diarization to work properly
MIN_AUDIO_DURATION_MS = 2000  # 2 seconds minimum


# =========================
# SPEAKER STORE
# =========================


class SpeakerStore:
    """
    Persistent speaker memory.
    Stores multiple embeddings per speaker.
    """

    def __init__(self, path: Path = SPEAKER_STORE_PATH):
        self.path = path
        self.speakers: dict[str, list[np.ndarray]] = {}

        if self.path.exists():
            with open(self.path, "rb") as f:
                self.speakers = pickle.load(f)

    def add_embedding(self, speaker_name: str, embedding: np.ndarray):
        if speaker_name not in self.speakers:
            self.speakers[speaker_name] = []

        self.speakers[speaker_name].append(embedding)
        self._save()

    def get_all(self):
        return self.speakers.items()

    def _save(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.speakers, f)


# =========================
# EMBEDDING MODEL
# =========================
store = SpeakerStore()


def audiosegment_to_embedding(chunk: AudioSegment) -> np.ndarray:
    """
    Convert an audio segment to a speaker embedding vector.

    Args:
        chunk: AudioSegment to convert

    Returns:
        Normalized embedding vector

    Raises:
        AudioProcessingError: If chunk is too short or processing fails
    """
    # Enforce minimum duration
    if len(chunk) < MIN_CHUNK_MS:
        raise AudioProcessingError(
            f"Chunk too short: {len(chunk)} ms (minimum: {MIN_CHUNK_MS} ms)"
        )

    # Force correct audio format
    chunk = (
        chunk.set_frame_rate(16000)  # Resample to 16kHz
        .set_channels(1)  # Convert to mono
        .apply_gain(-chunk.max_dBFS)  # Normalize volume
    )

    samples = np.array(chunk.get_array_of_samples()).astype("float32") / 32768.0

    if samples.shape[0] < 16000 * 2:
        raise AudioProcessingError("Too few samples for embedding (minimum: 2 seconds)")

    waveform = torch.from_numpy(samples).unsqueeze(0)

    try:
        embedding_model = ModelFactory.get_embedding_model()
        with torch.no_grad():
            embedding = embedding_model({"waveform": waveform, "sample_rate": 16000})
        return normalize(embedding)
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise AudioProcessingError(f"Failed to generate embedding: {e}") from e


# =========================
# SPEAKER IDENTIFICATION
# =========================


def identify_speaker(
    embedding: np.ndarray, store: SpeakerStore
) -> tuple[str | None, float]:
    """
    Compare an input embedding against known speakers using centroid similarity.
    Returns (speaker_name | None, similarity_score)
    """
    try:
        if embedding is None or not store.speakers:
            return None, 0.0

        best_score = -1.0
        best_speaker = None

        for speaker, embeddings in store.get_all():
            if not embeddings:
                continue

            # ---- compute centroid of stored embeddings ----
            centroid = np.mean(embeddings, axis=0)
            centroid = centroid / np.linalg.norm(centroid)

            # ---- cosine similarity ----
            score = cosine_similarity(
                embedding.reshape(1, -1),
                centroid.reshape(1, -1),
            )[0][0]

            logger.info(f"[SpeakerMatch] speaker={speaker}, score={score:.3f}")

            if score > best_score:
                best_score = score
                best_speaker = speaker

        logger.info(
            f"[SpeakerMatch] best_speaker={best_speaker}, "
            f"best_score={best_score:.3f}, "
            f"threshold={SIMILARITY_THRESHOLD}"
        )

        if best_score >= SIMILARITY_THRESHOLD:
            return best_speaker, float(best_score)

        return None, float(best_score)

    except Exception as e:
        logger.error(f"Error in identify_speaker: {e}")
        return None, 0.0


# =========================
# UTILITY (OPTIONAL)
# =========================


def identify_single_audio_chunk(
    chunk: AudioSegment, store: SpeakerStore
) -> tuple[str | None, float]:
    """
    Identify speaker for a standalone audio chunk.
    """

    # if len(chunk) < MIN_CHUNK_MS:
    #     return None, 0.0
    try:
        embedding = audiosegment_to_embedding(chunk)
        return identify_speaker(embedding, store)

    except Exception as e:
        logger.error(f"Error in identify_single_audio_chunk: {e}")
        return None, 0.0


def get_audio_duration(audio_path: str) -> float:
    """
    Get the duration of an audio file in milliseconds.

    Args:
        audio_path: Path to the audio file

    Returns:
        Duration in milliseconds

    Raises:
        AudioProcessingError: If audio file cannot be loaded
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        return len(audio)  # Returns duration in milliseconds
    except Exception as e:
        logger.error(f"Failed to get audio duration: {e}")
        raise AudioProcessingError(f"Failed to load audio file: {e}") from e


def diarize(audio_path: str) -> list[dict]:
    """
    Perform speaker diarization and transcription on an audio file.

    Args:
        audio_path: Path to the audio file

    Returns:
        List of dictionaries containing speaker segments with transcription

    Raises:
        AudioProcessingError: If diarization or transcription fails, or audio is too short
    """
    try:
        # Check audio duration before processing
        duration_ms = get_audio_duration(audio_path)
        duration_sec = duration_ms / 1000.0

        if duration_ms < MIN_AUDIO_DURATION_MS:
            raise AudioProcessingError(
                f"Audio file is too short ({duration_sec:.2f} seconds). "
                f"Minimum duration required: {MIN_AUDIO_DURATION_MS / 1000.0:.1f} seconds. "
                f"Please use a longer audio file for speaker identification."
            )

        logger.info(f"Processing audio file: {duration_sec:.2f} seconds")

        pipeline = ModelFactory.get_pipeline()
        whisper_model = ModelFactory.get_whisper_model()

        diarization = pipeline(audio_path)
        results = []
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000)

        # Check if diarization found any speakers
        speaker_turns = list(diarization.itertracks(yield_label=True))
        if not speaker_turns:
            logger.warning(
                "No speaker segments found in audio. "
                "This may happen with very short or silent audio files."
            )
            return results  # Return empty list instead of raising error

        for turn, _, speaker in speaker_turns:
            start = int(turn.start * 1000)
            end = int(turn.end * 1000)

            if end <= start:
                continue

            chunk = audio[start:end]
            samples = read(chunk)

            transcribed_result = whisper_model.transcribe(samples, fp16=False)
            text = transcribed_result.get("text", "").strip()

            results.append(
                {
                    "start_ms": start,
                    "end_ms": end,
                    "start_sec": round(turn.start, 3),
                    "end_sec": round(turn.end, 3),
                    "speaker": speaker,
                    "chunk": chunk,
                    "text": text,
                }
            )

        if not results:
            logger.warning("Diarization completed but no valid segments were extracted")

        return results
    except AudioProcessingError:
        # Re-raise AudioProcessingError as-is
        raise
    except Exception as e:
        logger.error(f"Error in diarize: {e}")
        raise AudioProcessingError(f"Diarization failed: {e}") from e


def read(audio_segment: AudioSegment) -> np.ndarray:
    """
    Convert AudioSegment to numpy array of normalized samples.

    Args:
        audio_segment: AudioSegment to convert

    Returns:
        Normalized float32 numpy array
    """
    y = np.array(audio_segment.get_array_of_samples())
    return np.float32(y) / 32768


def millisec(timeStr):
    spl = timeStr.split(":")
    return (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2])) * 1000)


def speakerIdentificationTool(audio_path: str) -> dict:
    """
    Identify speakers in an audio file by comparing against stored speaker embeddings.

    Args:
        audio_path: Path to the audio file to analyze

    Returns:
        Dictionary with success status, identified speakers, and events
    """
    audio_path = ensure_wav_16k_mono(audio_path)
    identified_speakers = set()
    events = []
    try:
        # Check audio duration first
        try:
            duration_ms = get_audio_duration(audio_path)
            duration_sec = duration_ms / 1000.0
            logger.info(f"Audio duration: {duration_sec:.2f} seconds")

            if duration_ms < MIN_AUDIO_DURATION_MS:
                return {
                    "success": False,
                    "error": (
                        f"Audio file is too short ({duration_sec:.2f} seconds). "
                        f"Minimum duration required: {MIN_AUDIO_DURATION_MS / 1000.0:.1f} seconds. "
                        f"Please use a longer audio file for speaker identification."
                    ),
                    "identified_speakers": [],
                    "details": {"total_speakers": 0},
                    "events": [
                        f"❌ Audio too short: {duration_sec:.2f}s "
                        f"(minimum: {MIN_AUDIO_DURATION_MS / 1000.0:.1f}s)"
                    ],
                }
        except AudioProcessingError as e:
            return {
                "success": False,
                "error": str(e),
                "identified_speakers": [],
                "details": {"total_speakers": 0},
                "events": [f"❌ Error: {str(e)}"],
            }

        transcribed_audio = diarize(audio_path)
        grouped_chunks = group_chunks_by_speaker(transcribed_audio)

        logger.info(f"Grouped chunks: {len(grouped_chunks)} speaker(s) found")

        if not grouped_chunks:
            logger.warning("No speaker segments found in audio file")
            return {
                "success": False,
                "error": (
                    "No speaker segments detected in the audio file. "
                    "This may happen if the audio is too short, silent, "
                    "or contains only background noise. "
                    f"Please ensure the audio is at least {MIN_AUDIO_DURATION_MS / 1000.0:.1f} seconds "
                    "and contains clear speech."
                ),
                "identified_speakers": [],
                "details": {"total_speakers": 0},
                "events": [
                    "⚠️ No speaker segments found in audio. "
                    "The audio may be too short or contain no speech."
                ],
            }

        # Process each speaker's chunks
        for diar_speaker, chunks in grouped_chunks.items():
            combined_chunk = sum(chunks)  # pydub concatenation
            logger.info(
                f"Processing {diar_speaker}: {len(combined_chunk)} ms "
                f"({len(chunks)} chunk(s))"
            )

            if len(combined_chunk) < MIN_CHUNK_MS:
                logger.warning(
                    f"Skipping {diar_speaker}, not enough audio "
                    f"({len(combined_chunk)} ms < {MIN_CHUNK_MS} ms)"
                )
                events.append(
                    f"⚠️ Skipped {diar_speaker}: audio segment too short "
                    f"({len(combined_chunk)} ms)"
                )
                continue

            try:
                identified_speaker, score = identify_single_audio_chunk(
                    combined_chunk, store
                )
                if identified_speaker:
                    events.append(
                        f"🗣 Identified speaker: {identified_speaker} "
                        f"(confidence {score:.2f})"
                    )
                    identified_speakers.add(identified_speaker)
            except AudioProcessingError as e:
                logger.warning(f"Failed to identify speaker for {diar_speaker}: {e}")
                events.append(f"⚠️ Could not identify {diar_speaker}: {str(e)}")
                continue

        if not identified_speakers:
            events.append(
                "⚠️ No speakers identified above confidence threshold "
                f"({SIMILARITY_THRESHOLD}). "
                "This may mean the speakers are not in the stored database, "
                "or the audio quality is insufficient."
            )

    except Exception as e:
        logger.error(f"Error in speakerIdentificationTool: {e}")
        return {
            "success": False,
            "error": str(e),
            "identified_speakers": [],
            "details": {"total_speakers": 0},
            "events": [f"❌ Error: {str(e)}"],
        }

    return {
        "success": True,
        "identified_speakers": sorted(identified_speakers),
        "details": {
            "total_speakers": len(identified_speakers),
        },
        "events": events,
    }


async def addSpeakerInStoreTool(audio_path: str, speakerName: str):
    try:
        diarized = diarize(audio_path)

        if not diarized:
            raise ValueError("No diarization output")

        # ---- group chunks by diarization speaker ----
        grouped = defaultdict(list)
        for item in diarized:
            grouped[item["speaker"]].append(item["chunk"])

        # ---- combine chunks & pick the longest one ----
        combined_chunks = {spk: sum(chunks) for spk, chunks in grouped.items()}

        diar_speaker, combined_audio = max(
            combined_chunks.items(),
            key=lambda x: len(x[1]),
        )

        logger.info(
            f"Selected chunk for storage: "
            f"{len(combined_audio)} ms (speaker={diar_speaker})"
        )

        # ---- enforce minimum duration ----
        if len(combined_audio) < MIN_CHUNK_MS:
            raise ValueError(
                f"Not enough audio to store speaker "
                f"({len(combined_audio)} ms) [Speaker Name] {speakerName} [File] {audio_path}"
            )

        # ---- extract embedding ----
        embedding = audiosegment_to_embedding(combined_audio)

        store.add_embedding(speakerName, embedding)

        logger.info(f"Stored embedding for speaker '{speakerName}'")

    except Exception as e:
        logger.error(f"Error in addSpeakerInStoreTool: {e}")
        return {"success": False, "error": str(e)}

    return {"success": True}


def normalize(emb: np.ndarray) -> np.ndarray:
    return emb / np.linalg.norm(emb)


def centroid(embeddings: list[np.ndarray]) -> np.ndarray:
    c = np.mean(embeddings, axis=0)
    return c / np.linalg.norm(c)


def group_chunks_by_speaker(diarized_chunks):
    grouped = defaultdict(list)

    for item in diarized_chunks:
        grouped[item["speaker"]].append(item["chunk"])

    return grouped
