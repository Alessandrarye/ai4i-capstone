# Phase 1: Concept Pitch (mid-September)

Format per George: ~2-minute spoken overview in breakout rooms. Nothing
required in hand. Goal is reaction and feedback, not approval. He suggests
bringing more than one idea.

## The 2-minute pitch (speak, don't read)

When a machine goes down unexpectedly in a small job shop, it can cost
hundreds of dollars an hour: scrapped parts, missed deliveries, emergency
service calls, days waiting for a regional technician. The frustrating part
is that machines usually announce failures in advance. Bearings run hotter,
torque climbs as tools dull. A veteran machinist can feel it, but nobody can
watch a dozen machines at once.

Big manufacturers solved this with predictive maintenance platforms, but
those assume enterprise budgets, cloud subscriptions, and streaming your
production data to someone else's servers. Small shops have none of that,
and often an active aversion to the last part.

I'm building the version for everyone else: a self-hosted platform that
watches machine sensor data (temperature, spindle speed, torque, tool wear)
and tells the owner which machine is likely to fail before it does. A
gradient-boosted classifier handles the known failure patterns, an anomaly
detector flags behavior it has never seen, and everything runs on a $300
fanless mini PC sitting inside the shop. No cloud, no subscription, no data
leaving the building.

For the capstone I'm training on the AI4I 2020 industrial dataset as a
stand-in for live telemetry, serving predictions through FastAPI with
Postgres storage, and showing it on a React dashboard built for at-a-glance
shop-floor monitoring. The demo goal for November: a live simulated shop
floor where you watch a machine's risk climb and an alert fire in real time.

Long term, this connects to where I'm headed personally: I'm also in a
manufacturing degree program, and the end goal is a software-integrated
machine shop. This is the first product of that.

## Anticipated breakout questions

- "Where does the data come from?" AI4I 2020 (UCI), built by an industrial
  AI researcher because real failure telemetry is commercially guarded.
  Real-shop pilot is the roadmap's phase 2.
- "Isn't this just thresholds?" The failure modes live in feature
  interactions (heat + low speed, wear x torque), and the model gives
  calibrated probabilities for scheduling, not binary panic.
- "Who would buy it?" Job shops with 5-50 machines and no reliability
  engineer. Planning owner interviews via my Purdue manufacturing
  instructors.

## Backup ideas (George: bring more than one)

1. Same platform, different data: SECOM semiconductor yield (real data,
   1,567 runs, 590 signals) or NASA CMAPSS remaining-useful-life. Platform,
   schema, and dashboard survive the swap.
2. Quality inspection pivot: casting defect photos (Kaggle, ~7,300 images),
   CNN behind the same FastAPI, upload-and-inspect UI. Same "affordable QC
   for small shops" story, different sense organ.
