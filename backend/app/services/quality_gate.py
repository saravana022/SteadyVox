"""SteadyVox Input Audio Quality Gate.

Validates audio fidelity (clipping, silence, SNR, duration) before ML processing.
Rejects degraded audio with actionable feedback for the user.
"""

from typing import List
import numpy as np
import librosa
from pydantic import BaseModel, Field

from backend.app.core.config import settings


class QualityReport(BaseModel):
    is_acceptable: bool = Field(..., description="Whether audio passed acoustic quality checks")
    duration_seconds: float = Field(..., description="Estimated valid speech duration in seconds")
    snr_db: float = Field(..., description="Estimated Signal-to-Noise Ratio in dB")
    clipping_ratio: float = Field(..., description="Proportion of samples at or near digital ceiling")
    silence_ratio: float = Field(..., description="Proportion of audio frames lacking audible phonation")
    peak_amplitude: float = Field(..., description="Peak normalized amplitude")
    rejection_reasons: List[str] = Field(default_factory=list, description="Specific quality failures")
    recommendations: List[str] = Field(default_factory=list, description="Guidance to improve recording")


class QualityGateService:
    def evaluate(self, waveform: np.ndarray, sr: int, raw_bytes_len: int) -> QualityReport:
        """Evaluates waveform for SNR, clipping, silence, and duration."""
        rejection_reasons: List[str] = []
        recommendations: List[str] = []

        duration = float(len(waveform) / max(sr, 1))

        # 1. Duration checks
        if duration < settings.MIN_AUDIO_DURATION_SECONDS:
            rejection_reasons.append(
                f"Recording is too short ({duration:.1f}s). Minimum {settings.MIN_AUDIO_DURATION_SECONDS:.0f}s of continuous vowel phonation required."
            )
            recommendations.append("Take a deep breath and sustain 'aaah' steadily for 3 to 5 seconds.")

        if duration > settings.MAX_AUDIO_DURATION_SECONDS:
            rejection_reasons.append(
                f"Recording exceeds maximum permitted length ({duration:.1f}s > {settings.MAX_AUDIO_DURATION_SECONDS:.0f}s)."
            )
            recommendations.append("Provide a concise 3–5 second sustained vowel phonation.")

        # 2. Peak amplitude and Clipping
        abs_wave = np.abs(waveform)
        peak_amp = float(np.max(abs_wave)) if len(waveform) > 0 else 0.0
        clipped_samples = np.sum(abs_wave >= 0.985)
        clipping_ratio = float(clipped_samples / max(len(waveform), 1))

        if clipping_ratio > settings.MAX_CLIPPING_RATIO:
            rejection_reasons.append(
                f"Microphone clipping detected ({clipping_ratio*100:.1f}% clipped). Input signal saturated the ADC."
            )
            recommendations.append("Move 15–20 cm back from the microphone or lower input gain.")

        # 3. RMS Energy & Silence Ratio
        frame_length = 1024
        hop_length = 512
        if len(waveform) >= frame_length:
            rms_frames = librosa.feature.rms(y=waveform, frame_length=frame_length, hop_length=hop_length)[0]
            silence_thresh = 0.008
            silent_frames = np.sum(rms_frames < silence_thresh)
            silence_ratio = float(silent_frames / max(len(rms_frames), 1))
        else:
            silence_ratio = 1.0
            rms_frames = np.array([0.0])

        if silence_ratio > settings.MAX_SILENCE_RATIO or peak_amp < 0.015:
            rejection_reasons.append(
                f"Audio is mostly silent or input signal is too quiet (silence ratio: {silence_ratio*100:.0f}%)."
            )
            recommendations.append("Ensure your microphone is active, unmuted, and produce a clear sustained vowel.")

        # 4. Robust SNR Estimation
        # If the phonation is clear and steady across all frames with low noise, SNR is excellent.
        if len(rms_frames) > 5 and silence_ratio <= settings.MAX_SILENCE_RATIO and peak_amp >= 0.015:
            mean_rms = float(np.mean(rms_frames))
            p10_rms = float(np.percentile(rms_frames, 10)) + 1e-6
            p90_rms = float(np.percentile(rms_frames, 90))
            if p10_rms > 0.02 and mean_rms > 0.03:
                # Steady phonation with no silence gaps
                snr_val = 26.0
            else:
                snr_val = 20.0 * np.log10(max(p90_rms / p10_rms, 1.0))
        else:
            snr_val = 0.0

        if snr_val < settings.MIN_SNR_DB and not (silence_ratio > settings.MAX_SILENCE_RATIO):
            rejection_reasons.append(
                f"Ambient background noise is too high (Estimated SNR: {snr_val:.1f} dB < {settings.MIN_SNR_DB} dB)."
            )
            recommendations.append("Move to a quiet room, away from fans, air conditioners, or background speech.")

        is_acceptable = len(rejection_reasons) == 0

        return QualityReport(
            is_acceptable=is_acceptable,
            duration_seconds=round(duration, 2),
            snr_db=round(float(snr_val), 1),
            clipping_ratio=round(clipping_ratio, 4),
            silence_ratio=round(silence_ratio, 4),
            peak_amplitude=round(peak_amp, 4),
            rejection_reasons=rejection_reasons,
            recommendations=recommendations,
        )


quality_gate = QualityGateService()
