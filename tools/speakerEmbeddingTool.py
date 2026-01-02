import logging
import pickle
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import torchaudio
import whisper
from pyannote.audio import Inference, Pipeline
from pydub import AudioSegment
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# CONFIGURATION
# =========================
logger = logging.getLogger(__name__)
SPEAKER_STORE_PATH = Path("speaker_store.pkl")

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")

whisper_model = whisper.load_model("small.en")


# similarity threshold (tune later)
SIMILARITY_THRESHOLD = 0.60

# minimum chunk length (ms) for reliable speaker ID
MIN_CHUNK_MS = 3000


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
embedding_model = Inference("pyannote/embedding", window="whole")


def audiosegment_to_embedding(chunk: AudioSegment) -> np.ndarray:
    # ---- enforce minimum duration ----
    if len(chunk) < MIN_CHUNK_MS:
        raise ValueError(f"Chunk too short: {len(chunk)} ms")

    # ---- force correct audio format ----
    chunk = (
        chunk.set_frame_rate(16000)  # REAL resample
        .set_channels(1)
        .apply_gain(-chunk.max_dBFS)
    )

    samples = np.array(chunk.get_array_of_samples()).astype("float32") / 32768.0

    if samples.shape[0] < 16000 * 2:
        raise ValueError("Too few samples for embedding")

    waveform = torch.from_numpy(samples).unsqueeze(0)

    with torch.no_grad():
        embedding = embedding_model({"waveform": waveform, "sample_rate": 16000})

    return normalize(embedding)


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


def diarize(audio_path):
    diarization = pipeline(audio_path)
    results = []  # 👈 this is what we will return
    audio = AudioSegment.from_mp3(audio_path)
    audio = audio.set_frame_rate(16000)

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start = int(turn.start * 1000)
        end = int(turn.end * 1000)

        if end <= start:
            continue

        chunk = audio[start:end]
        samples = read(chunk)

        transcribedResult = whisper_model.transcribe(samples, fp16=False)
        text = transcribedResult.get("text", "").strip()

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

    return results


def read(k):
    y = np.array(k.get_array_of_samples())
    return np.float32(y) / 32768


def millisec(timeStr):
    spl = timeStr.split(":")
    return (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2])) * 1000)


def speakerIdentificationTool(audio_path):
    audio, sr = torchaudio.load(audio_path)
    identified_speakers = set()
    events = []
    try:
        transcribedAudio = diarize(audio_path)
        grouped_chunks = group_chunks_by_speaker(transcribedAudio)

        if grouped_chunks:
            for diar_speaker, chunks in grouped_chunks.items():
                combined_chunk = sum(chunks)  # pydub concatenation
                if len(combined_chunk) < MIN_CHUNK_MS:
                    logger.warning(f"Skipping {diar_speaker}, not enough audio")

                identified_speaker, score = identify_single_audio_chunk(
                    combined_chunk, store
                )
                if identified_speaker:
                    final_speaker = identified_speaker

                    events.append(
                        f"🗣 Identified speaker: {identified_speaker} (confidence {score:.2f})"
                    )
                    identified_speakers.add(final_speaker)

    except Exception as e:
        logger.error(f"Error in voiceRecognitionAgent: {e}")
        return {"success": False, "error": str(e)}

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
