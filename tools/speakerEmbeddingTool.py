import logging
import pickle
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


def diarize(audio_path):
    logger.info("Enter in dial")
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
    store = SpeakerStore()
    events = []
    try:
        transcribedAudio = diarize(audio_path)
        if transcribedAudio:
            for audioChunk in transcribedAudio:
                identified_speaker, score = identify_single_audio_chunk(
                    audioChunk["chunk"], store
                )
                if identified_speaker:
                    final_speaker = identified_speaker

                    events.append(
                        f"🗣 Identified speaker: {identified_speaker} (confidence {score:.2f})"
                    )
                else:
                    final_speaker = audioChunk["speaker"]
                    embedding = audiosegment_to_embedding(audioChunk["chunk"])
                    store.add_embedding(final_speaker, embedding)
                    events.append(f"🆕 Learned new speaker: {final_speaker}")

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
