# Predictive Maintenance for Small Machine Shops

An edge-deployed predictive maintenance platform built for the UTD / Fullstack Academy AI/ML Bootcamp capstone. It watches a machine, learns what normal looks like, and warns the owner before something fails. Everything runs on one small computer on the shop floor: sensors, database, models, API, and dashboard. No cloud, no subscription.

**Author:** Sandra Hershey-Zagrans (GitHub: Alessandrarye)
**Demo:** November 12, 2026, live over Zoom with a physical sensor rig

---

## The problem

Small machine shops run equipment until it breaks because predictive maintenance is sold to large factories at $15,000 to $40,000 per deployment plus a subscription, and it assumes a reliability engineer on staff. A five-person shop is never in that conversation. This project proves the same capability can be delivered for about $70 in sensors per machine and one mini PC per shop. In production the sensors would be packaged industrial units at a few hundred dollars each, which is still roughly 100 times cheaper than the commercial option.

## What was built

| Layer | Implementation |
|---|---|
| Data and modeling | AI4I 2020 Predictive Maintenance dataset (Matzka, 2020). Feature engineering, stratified split, gradient-boosted classifier with class weighting and threshold tuning, Isolation Forest anomaly detector trained on healthy rows only. |
| Backend | FastAPI service that scores each reading with both models and stores it in PostgreSQL (Docker Compose, port 5433). |
| Dashboard | React + Vite. KPI cards, a green/yellow/red machine floor, status and trend charts, auto-refresh every few seconds. |
| Live sensor rig | ESP32 with an MPU-6050 accelerometer mounted on a desk fan, posting vibration readings over Wi-Fi to a dedicated `/live-reading` endpoint. Scored against a calibrated vibration baseline (0.07 watch, 0.12 fault). |
| Replay | `scripts/replay.py` streams the dataset through the live API to populate the dashboard with simulated machines. |

## Results on held-out data

Test set: 2,500 readings (25% stratified split, fixed seed), 85 real failures.

| Metric (failure class) | Value |
|---|---|
| Recall | 90.6% (77 of 85 failures caught) |
| Precision | 49.7% |
| F1 | 0.642 |
| Decision threshold | 0.046 (tuned on the precision-recall curve) |
| Confusion matrix | 2,337 true healthy, 78 false alarms, 8 missed failures, 77 caught |

Accuracy is 96.6%, which equals a model that always predicts "healthy." That is why accuracy is not reported as a success metric: with a 3.4% failure rate it says nothing. The threshold is deliberately low to favor recall, because for a shop owner a false alarm costs a five-minute walk and a missed failure costs a machine.

Permutation importance on the test set (PR-AUC drop when shuffled): rotational speed ≈ 0.43, temp_delta ≈ 0.41, power ≈ 0.27, tool wear ≈ 0.24, torque ≈ 0.04, type ≈ 0.02, raw air and process temperature ≈ 0. The engineered features carry the signal, which matches the failure physics (heat dissipation failures occur when the process-to-air gap is small at low speed).

Isolation Forest: trained on healthy readings only, threshold at the 2nd percentile of healthy scores (≈ -0.60), flagging about 2% of healthy readings and 15.3% of labeled failures per reading. It serves as the safety net for failure types the classifier was never trained on.

## Repository layout

```
ai4i-capstone/
├── backend/
│   └── app/
│       ├── main.py              FastAPI app
│       ├── database.py          SQLAlchemy / Postgres connection
│       ├── models.py            Reading table
│       ├── schemas.py           Pydantic request/response models
│       ├── ml/
│       │   ├── scorer.py        Loads both model bundles, scores a reading, maps to green/yellow/red
│       │   └── train_anomaly.py Trains the Isolation Forest on healthy rows
│       └── routes/
│           └── readings.py      /readings (dataset path) and /live-reading (sensor rig path)
├── frontend/                    React + Vite dashboard
├── models/
│   ├── failure_model_v0.1.joblib   Classifier bundle: model, threshold, feature list
│   └── anomaly_model_v0.1.joblib   Isolation Forest bundle
├── notebooks/
│   └── ai4i_baseline.ipynb      EDA, feature engineering, training, evaluation, importances
├── scripts/
│   └── replay.py                Streams the dataset through the API
├── data/                        AI4I 2020 CSV
├── docs/                        Proposal, roadmap, narrative paper
├── docker-compose.yml           PostgreSQL on port 5433
└── requirements.txt
```

ESP32 firmware (Arduino C++) samples the accelerometer, computes vibration features on the chip, and POSTs to `/live-reading` every few seconds. See the firmware folder or `docs/` for the sketch.

## How to run

Requirements: Python 3.12, Node 18+, Docker.

```bash
# 1. Database
docker compose up -d

# 2. Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd backend && uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend && npm install && npm run dev
# open http://localhost:5173

# 4. Populate the floor with simulated machines (new terminal)
python scripts/replay.py
```

To retrain the anomaly detector:

```bash
python backend/app/ml/train_anomaly.py --data data/ai4i2020.csv --out models/anomaly_model_v0.1.joblib
```

The classifier is trained and evaluated in `notebooks/ai4i_baseline.ipynb`, which writes `models/failure_model_v0.1.joblib`.

## How this maps to the capstone tasks

The bootcamp's reference capstone defines four stages. This project covers them as follows.

**Task 1, data preparation and exploration.** `notebooks/ai4i_baseline.ipynb`, sections 1 to 3. Loading, type standardization, distributions of each channel by class, the leakage rule (the five failure-mode columns define the target and never enter the feature matrix), identifier removal, two engineered physics features (temp_delta and power), and a stratified 75/25 split.

**Task 2, machine learning and predictive modeling.** Sections 4 to 8 of the notebook plus `train_anomaly.py`. A logistic-regression baseline, a gradient-boosted classifier with class weighting and threshold tuning, evaluation with precision, recall, F1, and the confusion matrix on held-out data, permutation importance, and an Isolation Forest anomaly detector. Both models are saved as versioned joblib bundles with their thresholds and feature contracts.

**Task 3, AI-driven analysis.** This project does not include an NLP or RAG layer. In its place it adds a layer the reference capstone does not have: a physical sensor rig feeding live readings into the same pipeline. The role of automated analysis is filled by the unsupervised anomaly detector (which flags failure types nobody labeled) and by the explainability work (permutation importance that matches the failure physics, so the output can be explained to a shop owner).

**Task 4, visualization and deployment.** FastAPI backend with inference endpoints, React dashboard, PostgreSQL in Docker Compose, replay tooling, and a live hardware demonstration. Deployed and tested locally on a desktop; migration to a dedicated mini PC is the next deployment step.

## Known limits

- The classifier is point-in-time. It flags whether a reading looks like a failure, not how long until one. Remaining-useful-life prediction needs time-series history the AI4I dataset does not contain.
- The AI4I dataset is synthetic, built to mimic a milling machine. The live rig exists partly to show the pipeline on real signals.
- The dataset features (temperature, speed, torque, wear) are not the rig's features (vibration), so the live rig is scored against a hand-calibrated vibration baseline rather than by the fitted models. Fitting the Isolation Forest on the rig's own history is the first modeling step after the demo.
- A desk fan is a fair stand-in for a motor with bearings, but it is not a CNC. Breadboard sensors are not shop sensors.
- No authentication on the dashboard or API yet. No staleness detection for a silent sensor yet. Both are on the roadmap.

## Next steps

1. Bring the temperature and current sensors back into the rig.
2. Fit the Isolation Forest on the rig's own vibration history.
3. Mount the system on a real CNC and learn that machine's baseline.
4. Collect time-series data and work toward lead-time (remaining-useful-life) estimates.
5. Authentication, staleness detection, and service hardening for a shop pilot.

## Reference

Matzka, S. (2020). Explainable artificial intelligence for predictive maintenance applications. *2020 Third International Conference on Artificial Intelligence for Industries (AI4I)*, 69–74. https://doi.org/10.1109/AI4I49448.2020.00023

AI coding assistants were used during development, as permitted by the course. All code is in this repository and fully visible.
