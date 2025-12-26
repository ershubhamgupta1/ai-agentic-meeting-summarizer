import logging

import numpy as np
import whisper
from pyannote.audio import Pipeline
from pydub import AudioSegment

logger = logging.getLogger(__name__)

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")

whisper_model = whisper.load_model("small.en")


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
