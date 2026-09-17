"""SteadyVox Audio Cleaning and Preprocessing Module.

Provides robust audio ingestion, mono conversion, silence trimming,
amplitude normalization, and fixed-length windowing for vocal analysis.

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Union, Optional
import numpy as np
import librosa
import soundfile as sf
import torch
import torchaudio


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    target_duration: float = 3.0  # seconds
    top_db_silence: float = 25.0
    normalize_peak: bool = True
    normalize_rms: bool = True
    target_rms: float = 0.10


def load_audio(
    file_path_or_bytes: Union[str, Path, bytes],
    target_sr: int = 16000,
    mono: bool = True,
) -> Tuple[np.ndarray, int]:
    """Load an audio file or raw bytes into a floating point NumPy waveform [-1.0, 1.0].
    
    Supports WAV, FLAC, MP3, OGG.
    """
    if isinstance(file_path_or_bytes, bytes):
        import io
        waveform, sr = sf.read(io.BytesIO(file_path_or_bytes), dtype='float32')
        if waveform.ndim > 1 and mono:
            waveform = np.mean(waveform, axis=1)
        if sr != target_sr:
            waveform = librosa.resample(waveform, orig_sr=sr, target_sr=target_sr)
            sr = target_sr
        return waveform.astype(np.float32), sr

    path = Path(file_path_or_bytes)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    waveform, sr = librosa.load(str(path), sr=target_sr, mono=mono)
    return waveform.astype(np.float32), sr


def trim_silence(
    waveform: np.ndarray,
    top_db: float = 25.0,
    frame_length: int = 2048,
    hop_length: int = 512,
) -> np.ndarray:
    """Trims leading and trailing silence from phonation recordings."""
    if len(waveform) == 0 or np.all(waveform == 0):
        return waveform

    trimmed, _ = librosa.effects.trim(
        waveform,
        top_db=top_db,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    # If trimmed is unexpectedly empty, return original
    return trimmed if len(trimmed) > 0 else waveform


def normalize_audio(
    waveform: np.ndarray,
    peak_norm: bool = True,
    rms_norm: bool = True,
    target_rms: float = 0.10,
    eps: float = 1e-8,
) -> np.ndarray:
    """Applies peak normalization and optional RMS energy normalization."""
    if len(waveform) == 0:
        return waveform

    normalized = waveform.copy()

    # Peak normalization
    if peak_norm:
        max_val = np.max(np.abs(normalized))
        if max_val > eps:
            normalized = normalized / max_val * 0.95

    # RMS normalization
    if rms_norm:
        current_rms = np.sqrt(np.mean(normalized ** 2))
        if current_rms > eps:
            scaling = target_rms / current_rms
            normalized = normalized * scaling
            # Safety clipping
            normalized = np.clip(normalized, -1.0, 1.0)

    return normalized.astype(np.float32)


def pad_or_truncate(
    waveform: np.ndarray,
    target_length: int,
    mode: str = "reflect",
) -> np.ndarray:
    """Ensures the waveform has exact target_length samples.
    
    If shorter, pads with reflection (or zeros).
    If longer, extracts the centered segment.
    """
    current_length = len(waveform)
    if current_length == target_length:
        return waveform

    if current_length > target_length:
        # Extract centered window
        start = (current_length - target_length) // 2
        return waveform[start : start + target_length]

    # Pad shorter audio
    pad_needed = target_length - current_length
    pad_left = pad_needed // 2
    pad_right = pad_needed - pad_left

    if mode == "reflect" and current_length > 1:
        # Librosa or numpy pad
        return np.pad(waveform, (pad_left, pad_right), mode="reflect").astype(np.float32)
    else:
        return np.pad(waveform, (pad_left, pad_right), mode="constant", constant_values=0.0).astype(np.float32)


def preprocess_pipeline(
    file_path_or_bytes: Union[str, Path, bytes],
    config: Optional[AudioConfig] = None,
) -> Tuple[np.ndarray, int]:
    """Complete preprocessing pipeline: load -> trim silence -> normalize -> fixed length window.
    
    Returns:
        waveform: 1D numpy array of shape (target_samples,)
        sample_rate: target sample rate in Hz
    """
    if config is None:
        config = AudioConfig()

    target_samples = int(config.sample_rate * config.target_duration)

    waveform, sr = load_audio(file_path_or_bytes, target_sr=config.sample_rate, mono=True)
    trimmed = trim_silence(waveform, top_db=config.top_db_silence)
    normalized = normalize_audio(
        trimmed,
        peak_norm=config.normalize_peak,
        rms_norm=config.normalize_rms,
        target_rms=config.target_rms,
    )
    processed = pad_or_truncate(normalized, target_length=target_samples)

    return processed, sr
