import logging
import pickle
from pathlib import Path

import numpy as np
import torch
from pyannote.audio import Inference
from pydub import AudioSegment
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# CONFIGURATION
# =========================
logger = logging.getLogger(__name__)
SPEAKER_STORE_PATH = Path("speaker_store.pkl")

# similarity threshold (tune later)
SIMILARITY_THRESHOLD = 0.75

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

embedding_model = Inference("pyannote/embedding", window="whole")


def audiosegment_to_embedding(chunk: AudioSegment) -> np.ndarray:
    """
    Convert AudioSegment -> speaker embedding
    """
    samples = np.array(chunk.get_array_of_samples()).astype("float32") / 32768.0
    waveform = torch.tensor(samples).unsqueeze(0)

    with torch.no_grad():
        embedding = embedding_model({"waveform": waveform, "sample_rate": 16000})

    return embedding


# =========================
# SPEAKER IDENTIFICATION
# =========================


def identify_speaker(
    embedding: np.ndarray, store: SpeakerStore
) -> tuple[str | None, float]:
    """
    Compare embedding against known speakers.
    Returns (speaker_name | None, similarity_score)
    """

    best_score = 0.0
    best_speaker = None

    for speaker, embeddings in store.get_all():
        for ref in embeddings:
            score = cosine_similarity(embedding.reshape(1, -1), ref.reshape(1, -1))[0][
                0
            ]

            if score > best_score:
                best_score = score
                best_speaker = speaker

    if best_score >= SIMILARITY_THRESHOLD:
        logger.info(
            f"best_score========{score, best_score, best_speaker, SIMILARITY_THRESHOLD}"
        )
        return best_speaker, best_score

    return None, best_score


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

    embedding = audiosegment_to_embedding(chunk)
    return identify_speaker(embedding, store)
