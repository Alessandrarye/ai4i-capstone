# Phase 2: Proposal Draft (early October)

George provides a Canvas template with questions. This pre-draft answers the
ones he named in class (compute, deliverable) plus the obvious ones, so the
template becomes a transpose job instead of a writing job.

## Problem statement

Unplanned equipment downtime costs small machine shops hundreds of dollars
per hour, and existing predictive maintenance tools are designed and priced
for enterprises. Small shops need failure prediction that is affordable,
private, and simple enough to run without a reliability engineer.

## Deliverable (what is actually being created)

A deployed, working application: a self-hosted predictive maintenance
platform. Concretely: a PostgreSQL database, a FastAPI service that ingests
sensor readings and scores them inline with a trained model, a React
dashboard showing per-machine failure risk with an alert feed, and a replay
script that streams the AI4I dataset through the system to simulate a live
shop floor. Delivered as a public GitHub repo with Docker Compose deployment
plus a live demo on November 11.

## Data

AI4I 2020 Predictive Maintenance Dataset (UCI, DOI 10.24432/C5HS5C): 10,000
machining cycles, 5 sensor channels plus machine type, binary failure label
(~3.4% positive) with five annotated failure modes. Already downloaded;
no scraping, labeling, or partner dependency.

## Modeling approach

- Target: binary machine failure. Failure-mode columns are excluded from
  features (they define the label; using them is leakage).
- Features: 5 sensors + type, plus physics-driven engineered features
  temp_delta (heat dissipation mechanism) and power (torque x angular
  velocity, power-band mechanism).
- Models: logistic regression baseline, then HistGradientBoosting with
  balanced class weights. SMOTE comparison included.
- Evaluation: precision/recall on the failure class and PR-AUC (accuracy is
  uninformative at 3.4% positives). Operating threshold chosen for ~90%
  recall with an explicit false-alarm budget; probability calibration
  checked before display.
- Stretch: Isolation Forest anomaly layer trained on healthy cycles to flag
  novel behavior the classifier has no category for.

## Compute resources needed

Minimal by design (part of the thesis). Training runs in seconds on CPU;
no GPU required. Development on my Ubuntu desktop, deployment target is a
fanless mini PC via Docker Compose. No cloud accounts or external services.

## MVP vs stretch goals

MVP (success = this works): baseline + tuned classifier, artifact behind
FastAPI, Postgres storing readings/predictions/alerts, dashboard with
per-machine risk and alert feed, replay-driven live demo.
Stretch, in cut order (first listed = first added, last cut): anomaly
detection layer, alert acknowledgment flow polish, explainer website
mirroring the dashboard, MQTT ingestion design note.

## Risks and mitigations

- Scope creep: MVP frozen above; stretch items have a declared cut order.
- Leakage: failure-mode columns quarantined from day one; notebook includes
  an explicit leakage section.
- Demo failure: entire stack runs locally via Docker Compose on the
  presentation laptop; a screen recording of the working demo is the backup.

## Timeline (working backwards from Nov 11)

- Sept: baseline notebook on real data; pitch; backend spine (ingest ->
  score -> store -> alert).
- Early Oct: proposal feedback loop with George; dashboard v1.
- Late Oct: threshold/calibration polish, scripted demo narrative, stretch
  goals as time allows; slide deck assembly from existing docs.
- Nov 1-9: rehearsal, practice session, freeze.
