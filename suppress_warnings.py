"""
Centralized warning suppression for Agentic AI stack.

This file suppresses known, safe, third-party warnings coming from:
- pyannote.audio
- torchaudio
- speechbrain
- pytorch_lightning
- torch
- gradio (deprecated constructor params)

IMPORTANT:
Import this file BEFORE importing any of the above libraries.
"""

import logging
import warnings


def suppress_third_party_warnings() -> None:
    # ------------------------------------------------------------------
    # Torchaudio backend deprecation warnings
    # ------------------------------------------------------------------
    warnings.filterwarnings(
        "ignore",
        message=".*set_audio_backend has been deprecated.*",
        category=UserWarning,
    )

    warnings.filterwarnings(
        "ignore",
        message=".*get_audio_backend has been deprecated.*",
        category=UserWarning,
    )

    # ------------------------------------------------------------------
    # SpeechBrain deprecated module path
    # ------------------------------------------------------------------
    warnings.filterwarnings(
        "ignore",
        message=".*speechbrain.pretrained.*deprecated.*",
        category=UserWarning,
    )

    # ------------------------------------------------------------------
    # torchaudio AudioMetaData import move
    # ------------------------------------------------------------------
    warnings.filterwarnings(
        "ignore",
        message=".*AudioMetaData.*moved to.*torchaudio.AudioMetaData.*",
        category=UserWarning,
    )

    # ------------------------------------------------------------------
    # PyTorch TypedStorage deprecation
    # ------------------------------------------------------------------
    warnings.filterwarnings(
        "ignore",
        message=".*TypedStorage is deprecated.*",
        category=UserWarning,
    )

    # ------------------------------------------------------------------
    # PyTorch Lightning checkpoint / migration noise
    # ------------------------------------------------------------------
    warnings.filterwarnings(
        "ignore",
        message=".*multiple `ModelCheckpoint` callback states.*",
        category=UserWarning,
    )

    warnings.filterwarnings(
        "ignore",
        message=".*Model was trained with pyannote.audio.*",
        category=UserWarning,
    )

    warnings.filterwarnings(
        "ignore",
        message=".*Model was trained with torch.*",
        category=UserWarning,
    )

    warnings.filterwarnings(
        "ignore",
        message=".*Found keys that are not in the model state dict.*",
        category=UserWarning,
    )

    # ------------------------------------------------------------------
    # Gradio deprecation warning (Blocks constructor params)
    # ------------------------------------------------------------------
    warnings.filterwarnings(
        "ignore",
        message=".*parameters have been moved from the Blocks constructor.*",
        category=UserWarning,
    )

    # ------------------------------------------------------------------
    # Optional: route remaining warnings to logging instead of stderr
    # ------------------------------------------------------------------
    logging.captureWarnings(True)
