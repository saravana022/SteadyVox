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

SteadyVox implements a **dual-path analysis pipeline** with an automated pre-flight **Audio Quality Gate**:

### Pre-Flight: Audio Quality Gate
Before passing audio into model inference, an automated signal hygiene gate evaluates the recording:
- **Duration**: Validates 1.0s – 12.0s sustained phonation
- **Signal-to-Noise Ratio (SNR)**: Enforces $\ge 9.0\text{ dB}$ (WADA-SNR algorithm)
- **Clipping Ratio**: Ensures digital saturation is $\le 3.0\%$
- **Silence Ratio**: Ensures active phonation is present ($\le 75\%$ silence)
- Rejects substandard audio with **RFC 7807 Problem Details** (HTTP 422) containing actionable recording recommendations.

### Path 1: Primary Clinical Model (Oxford Tabular MLP)
- **Clinical Provenance**: Trained on the real **Oxford Parkinson's Disease Dataset** (UCI ID 174, 195 clinical recordings from 31 subjects).
- **Feature Extraction**: Extracts 22 clinical acoustic biomarkers via **Praat/Parselmouth** ($F_0$, 5 Jitter metrics, 6 Shimmer metrics, HNR) combined with nonlinear recurrence dynamics (RPDE, DFA, Spread1/2, PPE).
- **Performance**: High clinical discrimination (**ROC-AUC 0.8925**, **F1 0.9487**).
- **Risk Stratification**: 3-tier clinical calibration:
  - `low` ($p < 0.40$): Low clinical risk indicator
  - `uncertain` ($0.40 \le p \le 0.70$): Indeterminate / borderline zone (repeat test recommended)
  - `elevated` ($p > 0.70$): Elevated acoustic dysphonia indicator

### Path 2: Secondary Acoustic Model (CNN + BiLSTM Benchmark)
- **Acoustic Spectrograms**: Time-preserving 2D Log Mel-Spectrograms processed through a **CNN + BiLSTM with Temporal Self-Attention**.
- **Role & Disclaimer**: Serves as an experimental benchmark trained on synthetic sustained phonations. Clearly labeled in every response as an ablation baseline; never substituted for clinical ground truth.

---

## 🏗️ Architecture & Data Flow

```
+─────────────────────────────────────────────────────────────────────────────+
│                       REACT + VITE FRONTEND (Nixtio UI)                     │
│    • Dark-first responsive layout (WCAG AA compliant, hairline borders)     │
│    • Live 16kHz mono audio recording with real-time VU level meter          │
│    • 3-tier risk badge, acoustic biomarker cards, RFC 7807 error toasts     │
│    • GDPR consent modal with audio retention opt-in/opt-out                 │
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │ POST /api/v1/screen
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
│                         NGINX REVERSE PROXY / INGRESS                       │
│                     Routes / -> Frontend, /api/ -> Backend                  │
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
                                       ▼
+─────────────────────────────────────────────────────────────────────────────+
│                            FASTAPI BACKEND API                              │
│                                                                             │
│  0. Request Tracing: Injects X-Request-ID and X-Process-Time-Ms             │
│  1. Audio Quality Gate: Validates duration, SNR, clipping, silence          │
│  2. Acoustic Extraction: 22 Praat biomarkers + Log Mel-Spectrogram          │
│  3. Dual-Path Inference: Oxford Tabular MLP (primary) + CNN+BiLSTM (second) │
│  4. Background Task: Asynchronous S3/MinIO upload without blocking client   │
│  5. Database: Async PostgreSQL with transparent SQLite fallback             │
│  6. Telemetry: Prometheus (/metrics) + stage latencies breakdown            │
+──────────────────────────────────────┬──────────────────────────────────────+
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
+───────────────────────────+                   +─────────────────────────────+
│    POSTGRESQL / SQLITE    │                   │      AWS S3 / MINIO         │
│  Screening sessions, risk │                   │ Raw audio recordings (.wav) │
│  SHA256, GDPR erasure API │                   │ Non-blocking async upload   │
+───────────────────────────+                   +─────────────────────────────+
```

---

## ⚡ Tech Stack Specification

| Domain | Technology | Version | Purpose |
|---|---|---|---|
| **Language** | Python | 3.11 / 3.12 | Core backend & ML pipelines |
| **Deep Learning** | PyTorch | 2.2+ | CNN & CNN+BiLSTM model training & inference |
| **Tabular ML** | Scikit-learn | Latest | Random Forest, MLP, Gradient Boosting |
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

## 📊 Multi-Dataset Model Benchmark Results

### Classification: Oxford Parkinson's Disease Detection (UCI ID 174)

195 recordings from 31 subjects. Binary classification (0=healthy, 1=PD). 80/20 stratified split, seed=42.

| Model | Accuracy | F1 (Weighted) | Precision | Recall | ROC-AUC |
|---|---|---|---|---|---|
| **Random Forest** | 0.9487 | **0.9501** | 0.9573 | 0.9487 | 0.9862 |
| **MLP Classifier** | 0.9487 | 0.9487 | 0.9487 | 0.9487 | **0.9931** |

### Regression: Parkinson's Telemonitoring (UCI ID 189)

5,875 recordings from 42 subjects. Predicting motor_UPDRS and total_UPDRS severity scores.

| Target | Model | RMSE | MAE | R² |
|---|---|---|---|---|
| motor_UPDRS | Gradient Boosting | 6.6932 | 5.4178 | 0.2981 |
| motor_UPDRS | **MLP Regressor** | **6.3818** | **5.0499** | **0.3619** |
| total_UPDRS | Gradient Boosting | 8.7888 | 6.9338 | 0.3029 |
| total_UPDRS | **MLP Regressor** | **8.2183** | **6.3457** | **0.3905** |

### Deep Learning: CNN Baseline vs CNN + BiLSTM (Synthetic Phonation)

Models evaluated on the held-out test split of unseen speakers (32 test samples, 50 total benchmark speakers):

| Architecture | Validation ROC-AUC | Test Accuracy (Nominal 0.5) | Test Recall (Calibrated) | Test F1 (Calibrated) |
|---|---|---|---|---|
| **2D CNN Baseline** | 0.6187 | 62.5% | 75.0% | 0.5294 |
| **CNN + BiLSTM (Temporal Attention)** | **0.7000** | 62.5% | 58.3% | 0.4516 |

> **Note:** The tabular ML path (Oxford Random Forest, ROC-AUC 0.9862) significantly outperforms the raw-audio CNN path because it operates on clinically validated extracted features from real patient data, whereas the CNN/BiLSTM models were trained on synthetic phonation signals. As real audio datasets become available, the deep learning path is expected to improve substantially.

---

---

## 🚀 Quick Start (Local Development)

### Option A: Native Localhost (One-Command Runner)
Run the full stack natively on your machine without needing Docker or external PostgreSQL:
```bash
git clone https://github.com/saravana/SteadyVox.git
cd SteadyVox
cp .env.example .env

# Start both FastAPI backend (with auto SQLite fallback) and Vite frontend:
bash start-localhost.sh
```
Access endpoints:
- **Web App**: http://localhost:5173
- **FastAPI Interactive Docs**: http://localhost:8000/docs
- **Backend Readiness**: http://localhost:8000/api/v1/ready

### Option B: Local Docker Compose Stack
```bash
docker compose -f infra/docker/docker-compose.dev.yml up -d --build
```
Access endpoints:
- **Frontend Dashboard**: http://localhost:5173
- **FastAPI Interactive Docs**: http://localhost:8000/docs
- **MinIO S3 Console**: http://localhost:9001 (User: `minioadmin` / Pass: `minioadmin`)
- **PostgreSQL Database**: `localhost:5432` (DB: `steadyvox_db`)

### Option C: Production Docker Stack with Observability
```bash
docker compose -f infra/docker/docker-compose.prod.yml up -d --build
```
Access endpoints:
- **SteadyVox Web App & API**: http://localhost:80
- **Prometheus UI**: http://localhost:9090
- **Grafana Monitoring Dashboard**: http://localhost:3000 (User: `admin` / Pass: `admin`)

---

## ☁️ AWS EC2 Deployment

### Prerequisites
- An AWS EC2 instance (Ubuntu 22.04+ recommended, t3.medium or larger)
- Security Group allowing inbound traffic on ports: **22** (SSH), **80** (HTTP), **443** (HTTPS), **9090** (Prometheus), **3000** (Grafana)
- SSH access to the instance

### One-Command Setup
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@13.201.193.223

# Clone and run setup
git clone https://github.com/saravana/SteadyVox.git /opt/steadyvox
cd /opt/steadyvox
sudo bash scripts/ec2-setup.sh
```

### Post-Deployment Endpoints
| Service | URL |
|---|---|
| **SteadyVox Web App** | http://13.201.193.223 |
| **FastAPI Docs** | http://13.201.193.223/docs |
| **Prometheus** | http://13.201.193.223:9090 |
| **Grafana** | http://13.201.193.223:3000 |

### CI/CD Auto-Deploy
Pushes to `main` trigger automatic deployment via GitHub Actions → SSH to EC2:

1. Set these GitHub repository secrets:
   - `EC2_HOST`: `13.201.193.223`
   - `EC2_USER`: `ubuntu`
   - `EC2_SSH_KEY`: Your EC2 private key (PEM format)

2. Every push to `main` will:
   - Run lint + tests (Python & Node.js)
   - Validate Docker Compose configs
   - SSH into EC2, pull latest code, rebuild & restart containers

---

## 🔬 Multi-Dataset ML Pipeline

SteadyVox includes a reproducible multi-dataset training pipeline that trains and evaluates models across three Parkinson's voice datasets:

### Datasets Used

| Dataset | UCI ID | Instances | Task | Features |
|---|---|---|---|---|
| **Oxford PD Detection** | 174 | 195 | Binary Classification | 22 voice features |
| **Istanbul PD Classification** | 470 | 252 | Binary Classification | 34 voice features |
| **Parkinson's Telemonitoring** | 189 | 5,875 | UPDRS Regression | 16 voice features |

> **Note:** The Istanbul dataset could not be automatically downloaded from UCI. Results shown are for Oxford and Telemonitoring only. To include Istanbul, manually place the CSV at `data/istanbul/parkinsons_classification.csv`.

### Running the Pipeline

```bash
# 1. Download datasets
python scripts/download_datasets.py

# 2. Exploratory Data Analysis
python notebooks/eda.py

# 3. Preprocess (StandardScaler, train/test splits)
python ml/preprocess.py

# 4. Train all models
python ml/train.py

# 5. Evaluate and generate comparison table
python ml/evaluate.py
# → results/comparison.md
```

Datasets are kept **separate** (no cross-dataset merging) to preserve experimental integrity. Each dataset gets its own StandardScaler, train/test split (80/20, seed=42), and trained models.

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
| `GET` | `/api/v1/health` | Service liveness health check & mandatory research disclaimer |
| `GET` | `/api/v1/ready` | Service readiness probe (database connectivity & model weights loaded) |
| `POST` | `/api/v1/screen` | **Primary dual-path screening**: audio quality gate, 22 Praat biomarkers, Oxford Tabular MLP + CNN/BiLSTM, async S3 persistence |
| `POST` | `/api/v1/screen/upload` | *(Deprecated)* Legacy upload route maintaining backward compatibility |
| `GET` | `/api/v1/history` | Paginated screening audit trail with 3-tier risk badges & SHA256 hashes |
| `GET` | `/api/v1/history/{id}` | Detailed session metrics, biomarker breakdown & quality report |
| `DELETE` | `/api/v1/history/{id}` | **GDPR Right-to-Erasure**: permanently purges session metadata & S3 audio |
| `GET` | `/api/v1/history/{id}/audio` | Stream or presigned URL redirect for recorded audio |
| `GET` | `/metrics` | Prometheus metrics scrape endpoint |

### Example cURL Request (Dual-Path Screening)
```bash
curl -X POST "http://localhost:8000/api/v1/screen" \
  -H "Accept: application/json" \
  -F "file=@sample_phonation.wav;type=audio/wav" \
  -F "patient_identifier=PATIENT-001" \
  -F "consent_given=true"
```

### Successful Response (`201 Created` / `200 OK`)
```json
{
  "session_id": "8f3b2a1c-...",
  "patient_identifier": "PATIENT-001",
  "audio_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "prediction": "parkinsons",
  "probability": 0.8124,
  "confidence": 0.8124,
  "risk_level": "elevated",
  "model_architecture": "Tabular MLP (Clinical Ground Truth)",
  "model_version": "2.1.0-oxford",
  "quality_report": {
    "passed": true,
    "duration_seconds": 3.42,
    "snr_db": 22.8,
    "clipping_ratio": 0.0001,
    "silence_ratio": 0.12,
    "recommendations": []
  },
  "primary_model": {
    "name": "Tabular MLP (Clinical Ground Truth)",
    "version": "2.1.0-oxford",
    "provenance": "Oxford Parkinson's Disease Dataset (UCI ML Repository, 195 recordings, Little et al.)",
    "risk_level": "elevated",
    "score": 0.8124
  },
  "secondary_model": {
    "name": "CNN + BiLSTM (Acoustic Spectrogram)",
    "version": "1.0.0-synthetic-benchmark",
    "provenance": "Sustained /a/ biophysical simulation benchmark (600 speakers, synthetic ablation)",
    "risk_level": "uncertain",
    "score": 0.542
  },
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
    "hnr_mean_db": 13.8,
    "rpde": 0.482,
    "dfa": 0.715,
    "ppe": 0.231
  },
  "stage_latencies": {
    "quality_gate_ms": 12.4,
    "acoustic_extraction_ms": 182.1,
    "primary_inference_ms": 0.8,
    "secondary_inference_ms": 22.3,
    "total_ms": 242.6
  },
  "latency_ms": 242.6,
  "disclaimer": "Research screening tool only — not a medical diagnosis. Consult a qualified neurologist."
}
```

### Audio Quality Gate Rejection (`422 Unprocessable Entity` — RFC 7807)
```json
{
  "type": "https://steadyvox.health/problems/audio-quality-degraded",
  "title": "Audio Quality Gate Check Failed",
  "status": 422,
  "detail": "Background noise level is too high (SNR: 6.2 dB < minimum 9.0 dB).",
  "instance": "/api/v1/screen",
  "invalid_params": [
    {
      "name": "snr_db",
      "reason": "Signal-to-noise ratio is 6.20 dB, below the acceptable threshold of 9.0 dB."
    }
  ],
  "recommendations": [
    "Move to a quieter room away from fans, air conditioning, and traffic.",
    "Hold the microphone approximately 10-15 cm (4-6 inches) from your mouth at a 45° angle."
  ]
}
```

---

## 📂 Project Structure

```
SteadyVox/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/endpoints/      # REST API route handlers
│   │   ├── core/               # Config, security, settings
│   │   ├── db/                 # SQLAlchemy models & session
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── services/           # Inference & storage services
│   ├── tests/                  # Backend unit tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # React 18 + Vite + TypeScript
│   ├── src/                    # Components, hooks, pages
│   ├── Dockerfile
│   └── package.json
├── ml/                         # Machine learning pipeline
│   ├── models/                 # PyTorch model architectures (CNN, BiLSTM)
│   ├── preprocessing/          # Audio feature extraction
│   ├── training/               # Training loops & hyperparameters
│   ├── data/                   # Dataset loaders & synthetic generation
│   ├── saved_models/           # Trained model checkpoints
│   ├── preprocess.py           # Multi-dataset preprocessing pipeline
│   ├── train.py                # Multi-dataset training pipeline
│   ├── evaluate.py             # Evaluation & comparison table generator
│   └── tests/                  # ML unit tests
├── scripts/
│   ├── download_datasets.py    # UCI dataset downloader (3 datasets)
│   └── ec2-setup.sh            # EC2 instance bootstrap script
├── notebooks/
│   └── eda.py                  # Exploratory data analysis
├── data/                       # Downloaded datasets (gitignored)
│   ├── oxford/
│   ├── istanbul/
│   └── telemonitoring/
├── results/
│   ├── comparison.md           # Multi-dataset model comparison table
│   └── comparison.json         # Raw evaluation metrics
├── infra/
│   ├── docker/
│   │   ├── docker-compose.dev.yml   # Local dev stack
│   │   └── docker-compose.prod.yml  # Production stack (EC2)
│   ├── nginx/                  # Reverse proxy config
│   ├── prometheus/             # Metrics scraping config
│   └── grafana/                # Dashboard provisioning
├── .github/workflows/ci.yml    # CI/CD pipeline (test → deploy EC2)
├── .env.example                # Environment variable template
└── README.md
```

---

## ⚠️ Disclaimers

1. **Not a Medical Device**: SteadyVox has not been evaluated, cleared, or approved by the FDA, EMA, CDSCO, or any other regulatory body. It is intended solely for research and educational purposes.

2. **No Clinical Advice**: The screening results, probability scores, and biomarker values produced by SteadyVox do not constitute medical advice, diagnosis, or treatment recommendations. Always consult a qualified healthcare provider for any medical concerns.

3. **Research Data Limitations**: Models trained on the Oxford dataset (195 samples, 31 subjects) and Telemonitoring dataset (5,875 samples, 42 subjects) may not generalize to broader populations. Performance metrics reflect held-out test set results and should be interpreted within the context of these specific datasets.

4. **Synthetic Training Data**: The CNN and CNN+BiLSTM deep learning models were trained on synthetically generated phonation signals, not real patient recordings. Their clinical utility has not been validated.

---

## 📚 Dataset Citations & References

1. **Little, M. A., McSharry, P. E., Roberts, S. J., Costello, D. A. E., & Moroz, I. M.** (2007). *Exploiting Nonlinear Recurrence and Fractal Scaling Properties for Voice Disorder Detection in Parkinson's Disease*. BioMedical Engineering OnLine, 6(1), 23. DOI: [10.1186/1475-925X-6-23](https://doi.org/10.1186/1475-925X-6-23)

2. **Sakar, C. O., Serbes, G., Gunduz, A., Tunc, H. C., Nour, H., Senim, A., ... & Apaydin, H.** (2019). *A Comparative Analysis of Speech Signal Processing Algorithms for Parkinson's Disease Classification and the Use of the Tunable Q-Factor Wavelet Transform*. Applied Soft Computing, 74, 255-263.

3. **Tsanas, A., Little, M. A., McSharry, P. E., & Ramig, L. O.** (2010). *Accurate Telemonitoring of Parkinson's Disease Progression by Noninvasive Speech Tests*. IEEE Transactions on Biomedical Engineering, 57(4), 884-893. DOI: [10.1109/TBME.2009.2036000](https://doi.org/10.1109/TBME.2009.2036000)

4. **Boersma, P., & Weenink, D.** (2021). *Praat: doing phonetics by computer* [Computer program]. Version 6.1.42. Retrieved from http://www.praat.org/

5. **UCI Machine Learning Repository** — Parkinson's Disease datasets. Retrieved from https://archive.ics.uci.edu/

---

## 📄 License

This project is provided for research and educational purposes. See [LICENSE](LICENSE) for details.
