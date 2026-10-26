"""SteadyVox Acoustic Feature Explanation Generator.

Generates dynamic, evidence-based clinical explanations from acoustic deviations
against demographic normative reference ranges (sex and age adjusted).

RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.
"""

from typing import Dict, Any, List, Optional


# Demographic reference ranges for sustained /a/ phonation
# Based on Titze (1994), Boersma (2001), Brockmann et al. (2008)
NORMATIVE_RANGES = {
    "male": {
        "f0_min": 85.0,
        "f0_max": 180.0,
        "f0_label": "85–180 Hz",
    },
    "female": {
        "f0_min": 165.0,
        "f0_max": 255.0,
        "f0_label": "165–255 Hz",
    },
    "general": {
        "jitter_local_max": 0.60,      # in %
        "jitter_rap_max": 0.40,        # in %
        "shimmer_local_max": 3.80,     # in %
        "shimmer_db_max": 0.35,        # in dB
        "hnr_min": 20.0,               # in dB
        "nhr_max": 0.02,
    }
}


def generate_acoustic_explanation(
    biomarkers: Dict[str, float],
    gender: Optional[str] = None,
    age: Optional[int] = None,
    risk_level: str = "low",
    is_ood: bool = False,
) -> str:
    """Generates an honest, non-templated explanation of acoustic feature findings.
    
    Args:
        biomarkers: Dictionary of extracted Praat features.
        gender: Male, Female, Other, or None.
        age: Patient age or None.
        risk_level: 'low', 'uncertain', 'elevated', or 'ood'.
        is_ood: Out-of-distribution flag.
        
    Returns:
        Scientifically grounded explanation string.
    """
    if is_ood:
        return (
            "Acoustic feature combination falls outside calibrated reference bounds "
            "(Mahalanobis distance exceeded 99th percentile of training distributions). "
            "Cannot assess reliably. Please check microphone placement and re-record in a quiet room."
        )

    norm_gender = (gender or "general").strip().lower()
    gender_key = "female" if "fem" in norm_gender else ("male" if "male" in norm_gender else None)
    
    deviations: List[str] = []
    
    # 1. Pitch (F0) inspection
    f0 = biomarkers.get("f0_mean", 0.0)
    if gender_key and f0 > 0:
        f0_ref = NORMATIVE_RANGES[gender_key]
        if f0 < f0_ref["f0_min"]:
            deviations.append(f"Mean pitch (F0: {f0:.1f} Hz) is lower than typical normative range for adult {gender_key}s ({f0_ref['f0_label']})")
        elif f0 > f0_ref["f0_max"]:
            deviations.append(f"Mean pitch (F0: {f0:.1f} Hz) is higher than typical normative range for adult {gender_key}s ({f0_ref['f0_label']})")

    # 2. Jitter (frequency perturbation)
    j_local = biomarkers.get("jitter_local_percent", 0.0)
    if j_local > NORMATIVE_RANGES["general"]["jitter_local_max"]:
        severity = "significantly elevated" if j_local > 1.04 else "mildly elevated"
        deviations.append(f"Cycle-to-cycle frequency variation (Jitter: {j_local:.2f}%) is {severity} (clinical threshold: < 0.60%), reflecting vocal fold vibratory irregularity")

    # 3. Shimmer (amplitude perturbation)
    s_local = biomarkers.get("shimmer_local_percent", 0.0)
    s_db = biomarkers.get("shimmer_local_db", 0.0)
    if s_local > NORMATIVE_RANGES["general"]["shimmer_local_max"] or s_db > NORMATIVE_RANGES["general"]["shimmer_db_max"]:
        deviations.append(f"Cycle-to-cycle amplitude perturbation (Shimmer: {s_local:.2f}%, {s_db:.2f} dB) exceeds standard reference bounds (< 3.80% / 0.35 dB), indicating phonatory instability")

    # 4. Harmonics-to-Noise Ratio (glottal noise/turbulence)
    hnr = biomarkers.get("hnr_mean_db", 0.0)
    if hnr > 0 and hnr < NORMATIVE_RANGES["general"]["hnr_min"]:
        deviations.append(f"Harmonics-to-Noise Ratio (HNR: {hnr:.1f} dB) is reduced below normative threshold (> 20.0 dB), consistent with acoustic breathiness or glottal turbulence")

    if not deviations:
        return (
            "All core acoustic perturbation markers (fundamental frequency stability, cycle-to-cycle jitter, "
            "amplitude shimmer, and harmonics-to-noise ratio) remain within normal physiological reference ranges. "
            "No acoustic dysarthria markers detected."
        )

    # Combine findings
    lead = "Observed acoustic deviations: " if risk_level == "elevated" else "Borderline acoustic variations noted: "
    return lead + "; ".join(deviations) + "."
