# AI4I Predictive Maintenance Platform

Capstone project: affordable, self-hosted predictive maintenance for small
machine shops. Sensor data in, calibrated failure-risk scores out, running
entirely on edge hardware inside the shop.

## Quick start

1. Open this folder in VS Code and reopen in the dev container when prompted
   (or run locally: `pip install -r requirements.txt`).
2. Download `ai4i2020.csv` (see `data/README.md`) into `data/`.
3. Open `notebooks/ai4i_baseline.ipynb` and run top to bottom. It saves a
   model artifact to `models/`.

## Layout

- `notebooks/`  EDA and model experiments (notebook-first, promoted to backend/app/ml when stable)
- `backend/`    FastAPI service: ingestion, scoring, alerts (in progress)
- `frontend/`   React dashboard (in progress)
- `scripts/`    replay.py streams the CSV through the API to simulate live sensors
- `docs/`       narrative paper, pitch, proposal draft, roadmap
- `data/`       raw dataset (gitignored)
- `models/`     trained model artifacts (gitignored)

## Capstone phases

1. Concept pitch (mid-September): `docs/pitch.md`
2. Proposal (early October): `docs/proposal-draft.md`, transposed into the Canvas template
3. Roadmap: `docs/roadmap.md`
4. Demo day (November 11): live demo + slides

Dataset: Matzka, S. (2020). AI4I 2020 Predictive Maintenance Dataset.
UCI Machine Learning Repository. https://doi.org/10.24432/C5HS5C
