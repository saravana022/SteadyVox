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

SteadyVox implements a **dual-path analysis pipeline**:

### Path 1: Deep Learning on Raw Audio (CNN + BiLSTM)
- Time-preserving 2D Log Mel-Spectrograms processed through a **CNN + BiLSTM with Temporal Self-Attention**
- Captures vocal tremor dynamics (4–7 Hz modulation) and phonation decay over time
- Extracts clinical acoustic perturbations: Fundamental frequency ($F_0$), Jitter, Shimmer, and HNR via **Praat / Parselmouth**

### Path 2: Tabular ML on Extracted Voice Features (Random Forest + MLP)
- Trained on the **Oxford Parkinson's Disease Detection Dataset** (UCI ID 174, 195 recordings, 31 subjects)
- Also evaluated on the **Parkinson's Telemonitoring Dataset** (UCI ID 189, 5,875 recordings, 42 subjects)
- Uses extracted voice perturbation features (Jitter, Shimmer, HNR, RPDE, DFA, PPE, etc.)
- Random Forest and MLP classifiers for binary PD detection; Gradient Boosting and MLP regressors for UPDRS severity prediction

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
| `GET` | `/api/v1/health` | Service health status and research disclaimer |
| `POST` | `/api/v1/screen/upload` | Upload audio phonation (`.wav`/`.mp3`), run CNN+BiLSTM inference, extract Praat biomarkers, persist to PostgreSQL and S3 |
| `GET` | `/api/v1/history` | Paginated list of past screening sessions |
| `GET` | `/api/v1/history/{id}` | Detailed metrics for a specific screening session |
| `GET` | `/api/v1/history/{id}/audio` | Stream or presigned URL redirect for recorded audio |
| `GET` | `/metrics` | Prometheus metrics scrape endpoint |

### Example cURL Request
```bash
curl -X POST "http://13.201.193.223/api/v1/screen/upload" \
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
