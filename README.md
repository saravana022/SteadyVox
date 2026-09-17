# SteadyVox: AI-Powered Deep Neural Voice Analysis for Parkinson's Disease Screening

[![CI/CD](https://github.com/saravana/SteadyVox/actions/workflows/ci.yml/badge.svg)](https://github.com/saravana/SteadyVox/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![PyTorch 2.2+](https://img.shields.io/badge/PyTorch-2.2+-ee4c2c.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ed.svg)](https://www.docker.com/)

> ⚠️ **RESEARCH SCREENING TOOL ONLY — NOT A MEDICAL DIAGNOSIS.**  
> SteadyVox is an investigational machine learning platform designed to analyze vocal acoustic biomarkers for research and screening triaging. It is **not** an FDA/CE-approved medical device, cannot provide medical advice, and must never be used as a standalone clinical diagnosis. Every user interface, API response, and generated report explicitly reflects this non-diagnostic notice.

---

## 🔬 Overview & Scientific Rationale

Parkinson's Disease (PD) is a progressive neurodegenerative disorder caused by the depletion of dopaminergic neurons in the *substantia nigra pars compacta*. Hypokinetic dysarthria—characterized by vocal tremor, reduced loudness, monopitch, breathiness, and articulatory imprecision—often emerges years before noticeable gross motor tremors.

SteadyVox evaluates both:
1. **Spectral Representations via Deep Learning**: Time-preserving 2D Log Mel-Spectrograms processed through a **CNN + BiLSTM with Temporal Self-Attention** to capture vocal tremor dynamics (4–7 Hz modulation) and phonation decay over time.
2. **Clinical Acoustic Perturbations**: Fundamental frequency ($F_0$), Jitter (cycle-to-cycle frequency variation), Shimmer (cycle-to-cycle amplitude perturbation), and Harmonics-to-Noise Ratio (HNR) extracted using **Praat / Parselmouth** algorithms.

---

## 🏗️ Architecture & Data Flow

```
+─────────────────────────────────────────────────────────────────────────────+
│                           REACT + VITE FRONTEND                             │
│     Live 5s Phonation Audio Recording (Web Audio API) or WAV/MP3 Upload    │
│            Prominent Non-Diagnostic Research Disclaimer Banner              │
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │ POST /api/v1/screen/upload
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
│                             NGINX REVERSE PROXY                             │
│                     Routes / -> Frontend, /api/ -> Backend                  │
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
│                            FASTAPI BACKEND API                              │
│                                                                             │
│  1. Signal Cleaning: Mono convert, resample to 16kHz, silence trim, RMS norm│
│  2. Acoustic Extraction: Praat (Jitter, Shimmer, HNR, F0) + Log Mel-Spec    │
│  3. Model Inference: CNN + BiLSTM with Temporal Attention                   │
│  4. Data Persistence: PostgreSQL (session metadata) + AWS S3/MinIO (audio)  │
│  5. Telemetry: Prometheus Metrics (/metrics) -> Grafana Monitoring Dashboard│
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
+───────────────────────────+                   +─────────────────────────────+
│    POSTGRESQL DATABASE    │                   │      AWS S3 / MINIO         │
│  Screening sessions, risk │                   │ Raw audio recordings (.wav) │
│  confidence, biomarkers   │                   │ Presigned URL streaming     │
+───────────────────────────+                   +─────────────────────────────+
```

---

## ⚡ Tech Stack Specification

| Domain | Technology | Version | Purpose |
|---|---|---|---|
| **Language** | Python | 3.11 / 3.12 | Core backend & ML pipelines |
| **Deep Learning** | PyTorch | 2.2+ | CNN & CNN+BiLSTM model training & inference |
| **Audio Processing** | Librosa, SoundFile, TorchAudio | 0.10+ | Spectrograms, MFCCs, audio preprocessing |
| **Voice Pathology** | Praat-Parselmouth | 0.4.3+ | Clinical Jitter, Shimmer, HNR, F0 calculations |
| **Data Processing** | NumPy, Pandas, SciPy | Latest | Phonation modeling and feature vectors |
| **Evaluation** | Scikit-learn, Matplotlib | Latest | ROC-AUC, confusion matrix, and threshold calibration |
| **Backend API** | FastAPI, Uvicorn | 0.110+ | Asynchronous REST API, auto OpenAPI docs |
| **Database** | PostgreSQL | 15 (Alpine) | Session metadata, patient IDs, biomarker records |
| **Object Store** | AWS S3 / MinIO | Latest | S3-compatible raw audio storage |
| **Frontend UI** | React 18 + TypeScript + Vite | Latest | Interactive audio recorder & diagnostic dashboard |
| **Styling & Icons** | Tailwind CSS, Lucide React | Latest | Modern responsive UI |
| **Reverse Proxy** | Nginx | Alpine | Reverse proxy, static asset serving, SSL termination |
| **Monitoring** | Prometheus + Grafana | Latest | Latency, throughput, and screening volume metrics |
| **CI/CD** | GitHub Actions | v4 | Automated linting, testing, Docker validation, EC2 deploy |

---

## 📊 Model Benchmark: CNN Baseline vs CNN + BiLSTM

Models evaluated on the held-out test split of unseen speakers (32 test samples, 50 total benchmark speakers):

| Architecture | Validation ROC-AUC | Test Accuracy (Nominal 0.5) | Test Recall (Calibrated) | Test F1 (Calibrated) |
|---|---|---|---|---|
| **2D CNN Baseline** | 0.6187 | 62.5% | 75.0% | 0.5294 |
| **CNN + BiLSTM (Temporal Attention)** | **0.7000** | 62.5% | 58.3% | 0.4516 |
| **Delta** | **+0.0813 (+8.13%)** | -- | -- | -- |

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/saravana/SteadyVox.git
cd SteadyVox
cp .env.example .env
```

### 2. Run Local Multi-Service Development Stack (Docker Compose)
```bash
docker compose -f infra/docker/docker-compose.dev.yml up -d --build
```
Access endpoints:
- **Frontend Dashboard**: http://localhost:5173
- **FastAPI Interactive Docs**: http://localhost:8000/docs
- **MinIO S3 Console**: http://localhost:9001 (User: `minioadmin` / Pass: `minioadmin`)
- **PostgreSQL Database**: `localhost:5432` (DB: `steadyvox_db`)

### 3. Run Production Stack with Prometheus & Grafana
```bash
docker compose -f infra/docker/docker-compose.prod.yml up -d --build
```
Access endpoints:
- **SteadyVox Web App & API**: http://localhost:80
- **Prometheus UI**: http://localhost:9090
- **Grafana Monitoring Dashboard**: http://localhost:3000 (User: `admin` / Pass: `admin`)

---

## 🧪 Running Automated Tests

Run the complete test suite across ML preprocessing, CNN/BiLSTM models, and FastAPI backend:
```bash
# Run all unit tests
pytest -v
```

Output:
```
backend/tests/test_api.py::test_health_check_endpoint PASSED             [  6%]
backend/tests/test_api.py::test_root_endpoint PASSED                     [ 12%]
backend/tests/test_api.py::test_screen_upload_endpoint PASSED            [ 18%]
backend/tests/test_api.py::test_history_endpoint PASSED                  [ 25%]
ml/tests/test_dataset.py::test_generate_phonation_sample PASSED          [ 31%]
ml/tests/test_dataset.py::test_dataset_pipeline PASSED                   [ 37%]
ml/tests/test_features.py::test_pad_or_truncate PASSED                   [ 43%]
ml/tests/test_features.py::test_normalize_audio PASSED                   [ 50%]
ml/tests/test_features.py::test_extract_mel_spectrogram PASSED           [ 56%]
ml/tests/test_features.py::test_extract_mfcc PASSED                      [ 62%]
ml/tests/test_features.py::test_extract_biomarkers PASSED                [ 68%]
ml/tests/test_features.py::test_extract_model_features PASSED            [ 75%]
ml/tests/test_model.py::test_cnn_baseline_forward PASSED                 [ 81%]
ml/tests/test_model.py::test_cnn_baseline_predict_proba PASSED           [ 87%]
ml/tests/test_model.py::test_cnn_feature_extraction PASSED               [ 93%]
ml/tests/test_model.py::test_cnn_bilstm_forward PASSED                   [100%]
======================== 16 passed, 1 warning in 7.01s =========================
```

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health status and research disclaimer |
| `POST` | `/api/v1/screen/upload` | Upload audio phonation (`.wav`/`.mp3`), run CNN+BiLSTM inference, extract Praat biomarkers, persist to PostgreSQL and S3 |
| `GET` | `/api/v1/history` | Paginated list of past screening sessions |
| `GET` | `/api/v1/history/{id}` | Detailed metrics for a specific screening session |
| `GET` | `/api/v1/history/{id}/audio` | Stream or presigned URL redirect for recorded audio |
| `GET` | `/metrics` | Prometheus metrics scrape endpoint |

### Example cURL Request
```bash
curl -X POST "http://localhost:8000/api/v1/screen/upload" \
  -F "file=@sample_phonation.wav;type=audio/wav" \
  -F "patient_identifier=PATIENT-001"
```

Response:
```json
{
  "session_id": "8f3b2a1c-...",
  "patient_identifier": "PATIENT-001",
  "prediction": "parkinsons",
  "probability": 0.521,
  "confidence": 0.521,
  "model_architecture": "cnn_bilstm",
  "biomarkers": {
    "f0_mean": 134.2,
    "f0_std": 14.8,
    "f0_min": 110.0,
    "f0_max": 160.0,
    "jitter_local_percent": 2.45,
    "jitter_rap_percent": 1.47,
    "jitter_ppq5_percent": 1.96,
    "shimmer_local_percent": 7.82,
    "shimmer_local_db": 0.65,
    "shimmer_apq3_percent": 3.91,
    "shimmer_apq5_percent": 5.47,
    "hnr_mean_db": 13.8
  },
  "latency_ms": 142.5,
  "disclaimer": "Research screening tool only — not a medical diagnosis."
}
```

---

## 📚 Dataset Citations & References
1. **Little, M. A., et al.** (2007). *Exploiting Nonlinear Recurrence and Fractal Scaling Properties for Voice Disorder Detection in Parkinson's Disease*. BioMedical Engineering OnLine, 6(1), 23.
2. **Boersma, P., & Weenink, D.** (2021). *Praat: doing phonetics by computer* [Computer program]. Version 6.1.42.
3. **Italian Parkinson's Voice and Speech Dataset** (IEEE DataPort / Zenodo).
4. **Tsanas, A., et al.** (2012). *Novel Speech Signal Processing Algorithms for High-Accuracy Classification of Parkinson's Disease*. IEEE Transactions on Biomedical Engineering, 59(5), 1264-1271.
