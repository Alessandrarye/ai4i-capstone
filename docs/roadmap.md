# Phase 3: Roadmap (ordered steps, MVP first)

Format per George: what happens first, second, third to reach a viable
demo (MVP), then stretch. Dates optional; order is the point.

## Sprint to MVP

1. Run baseline notebook on real AI4I data; record metrics and failure-mode
   breakdown. (Notebook already built and tested.)
2. Postgres schema up via Docker Compose: machines, readings, predictions
   (with model_version), alerts.
3. FastAPI spine: POST /readings does store -> score -> store prediction ->
   fire alert in one request. GET /machines, GET /machines/{id},
   GET /alerts, POST /alerts/{id}/ack, GET /health.
4. Replay script POSTs CSV rows on an interval; verify end-to-end flow in
   the API docs page.
5. Dashboard v1: machine cards with risk gauge, alert feed, acknowledge
   button, polling every few seconds.
6. Scripted demo: pick one machine whose readings degrade convincingly;
   rehearse the two-minute "watch Machine 7" narrative.
   <- FLAG PLANTED. Everything below is bonus.

## Stretch (in order added; reverse order cut)

7. Isolation Forest anomaly layer trained on healthy cycles; "unusual
   behavior" flag on the dashboard, distinct from failure risk.
8. Threshold/calibration polish and a model-comparison page (logreg vs GB,
   PR curves) for the technical appendix.
9. Explainer website mirroring the dashboard for non-technical audiences.
10. MQTT ingestion design note: what phase 2 with a real shop looks like.

## Beyond the capstone (roadmap slide material)

Real sensor ingestion with a design-partner shop -> remaining useful life
(regression, CMAPSS-style) -> drift detection and local retraining ->
multi-shop transfer/federated learning; vibration/acoustic sensors open the
deep learning chapter.
