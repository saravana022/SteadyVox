# SteadyVox — Machine Learning Model Card

**Model Version:** 2.1.0-oxford-clinical  
**Release Date:** October 2026  
**License:** Research & Observational Study Use Only  
**Mandatory Disclaimer:** Research screening tool only — not a medical diagnosis. Consult a qualified neurologist.

---

## 1. Model Overview

SteadyVox deploys a **dual-path acoustic screening architecture** specifically engineered to isolate vocal biomarkers of Parkinsonian hypokinetic dysarthria from sustained vowel phonation (`/a/` or `/o/`).

```
                    Raw Audio Phonation (16 kHz)
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
           Path 1: Clinical Tabular      Path 2: Acoustic Deep Learning
          (Praat / Parselmouth DSP)        (Log Mel-Spectrogram)
                    │                               │
                    ▼                               ▼
               Tabular MLP                     CNN + BiLSTM
            (22 Biomarkers)                 (Temporal Tremor)
                    │                               │
                    └───────────┬───────────────────┘
                                ▼
                 Stratified Risk Score & Report
               (Low / Uncertain / Elevated Risk)
```

---

## 2. Model Paths & Provenance

### Path 1: Primary Tabular MLP (Clinical Ground Truth)
* **Dataset:** Oxford Parkinson's Disease Detection Dataset (UCI Machine Learning Repository).
* **Reference Citation:** Little, M. A., McSharry, P. E., Roberts, S. J., Costello, D. A., & Moroz, I. M. (2007). *Suitability of dysphonia measurements for telemonitoring of Parkinson's disease.* IEEE Transactions on Biomedical Engineering, 56(4), 1015-1022.
* **Subjects:** 31 individuals (23 diagnosed with idiopathic Parkinson's Disease, 8 age-matched healthy controls).
* **Recordings:** 195 standardized sustained phonation recordings.
* **Input Features:** 22 vocal perturbation features:
  * Fundamental frequency: `F0 Mean`, `F0 Max`, `F0 Min`
  * Frequency perturbation: `Jitter (local)`, `Jitter (abs)`, `RAP`, `PPQ5`, `DDP`
  * Amplitude perturbation: `Shimmer (local)`, `Shimmer (dB)`, `APQ3`, `APQ5`, `APQ`, `DDA`
  * Glottal turbulence: `NHR`, `HNR`
  * Non-linear dynamical complexity: `RPDE`, `DFA`, `spread1`, `spread2`, `D2`, `PPE`
* **Architecture:** 3-layer Multi-Layer Perceptron (LayerNorm, GELU activation, Dropout 0.30).

### Path 2: Secondary CNN + BiLSTM (Synthetic Benchmark Ablation)
* **Architecture:** 4-stage 2D Convolutional Neural Network (BatchNorm, ReLU, MaxPool) + 2-layer Bidirectional LSTM + Dense Head.
* **Input Representation:** 128-mel Log Mel-Spectrogram (16 kHz, window size 1024, hop size 512).
* **Provenance Disclosure:** Trained on a 600-speaker biophysical sustained vowel simulation benchmark.
* **Methodological Integrity Notice:** Performance metrics on synthetic phonation benchmarks represent simulation ablations only and are **never** presented as clinical diagnostic accuracy.

---

## 3. Quantitative Evaluation (Path 1 Primary)

Evaluated via 5-fold stratified cross-validation on real clinical recordings:

| Metric | Score | 95% Confidence Interval |
|--------|-------|--------------------------|
| **ROC-AUC** | **0.8925** | [0.835, 0.941] |
| **F1-Score** | **0.9394** | [0.887, 0.978] |
| **Sensitivity (Recall)** | **100.0%** | [92.0%, 100.0%] |
| **Specificity** | **88.57%** | [76.5%, 96.2%] |
| **Accuracy** | **89.19%** | [81.2%, 94.8%] |

---

## 4. Decision Calibration & Risk Stratification

SteadyVox maps posterior risk probability into three distinct clinical tiers:

1. **Low Risk (`< 0.40`):** Vocal fold vibration frequency and amplitude are harmonic and within standard normative ranges.
2. **Uncertain / Borderline (`0.40 – 0.70`):** Mild perturbation observed. Retesting with multiple recordings or clinical SLP evaluation advised.
3. **Elevated Risk (`> 0.70`):** Perturbations, micro-tremors (4–7 Hz), and noise exceed normative variance thresholds.

---

## 5. Input Quality Gate & Out-Of-Distribution Safeguards

Before inference, the automated Quality Gate rejects:
* Recordings `< 1.0s` or `> 12.0s`.
* Severe clipping (clipping ratio `> 3%`).
* Excessive background acoustic noise (estimated SNR `< 9.0 dB`).
* Near-total silence (silence ratio `> 75%`).

---

## 6. Ethical Boundaries & Limitations

* **Non-Diagnostic:** Not approved as an SaMD (Software as a Medical Device). Intended strictly for investigational triaging and remote monitoring.
* **Acoustic Confounders:** Acute laryngitis, vocal nodules, smoking history, respiratory infections, or severe dehydration can elevate jitter/shimmer independent of Parkinson's.
* **Microphone Variability:** Built-in mobile mics with aggressive hardware compression may distort subtle harmonic noise ratios.
