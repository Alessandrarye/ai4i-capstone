"""
Train the anomaly detector (Isolation Forest) for the predictive-maintenance pipeline.

It trains on HEALTHY readings only, so the model learns what normal operation looks
like and flags anything that deviates from it, including failure types the supervised
classifier was never trained on. This is the unsupervised half of the dual-model design.

Run from the repo root on foundry (adjust --data if your csv lives elsewhere):

    python ml/train_anomaly.py
    python ml/train_anomaly.py --data data/ai4i2020.csv --out ml/anomaly_model_v0.1.joblib

It writes a joblib bundle shaped like your classifier bundle, so the scorer loads it
the same way:

    {model, threshold, features, categorical, model_version}
"""

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

# The same feature contract the classifier uses, so one reading feeds both models.
NUMERIC = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "temp_delta",
    "power",
]
CATEGORICAL = ["Type"]
FEATURES = CATEGORICAL + NUMERIC

# Flag readings that fall below this percentile of the healthy score distribution.
# Lower = fewer alerts (stricter). 2.0 means about 2% of normal readings would flag.
HEALTHY_PERCENTILE = 2.0
MODEL_VERSION = "iforest-v0.1"


def add_engineered(df: pd.DataFrame) -> pd.DataFrame:
    """Add the same two engineered features the classifier expects."""
    df = df.copy()
    df["temp_delta"] = df["Process temperature [K]"] - df["Air temperature [K]"]
    df["power"] = df["Torque [Nm]"] * df["Rotational speed [rpm]"] * 2 * math.pi / 60
    return df


def build_pipeline() -> Pipeline:
    # Select columns by name so input column order never matters at inference time.
    pre = ColumnTransformer(
        transformers=[
            ("type", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ],
        remainder="drop",
    )
    iforest = IsolationForest(
        n_estimators=300,
        max_samples="auto",
        contamination="auto",   # we set our own threshold below, so this is just the fit offset
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline([("pre", pre), ("iforest", iforest)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/ai4i2020.csv", help="path to the AI4I csv")
    ap.add_argument("--out", default="ml/anomaly_model_v0.1.joblib", help="output bundle path")
    args = ap.parse_args()

    df = pd.read_csv(args.data)
    df = add_engineered(df)

    # Healthy rows only. Machine failure == 0 is the normal-operation baseline.
    healthy = df[df["Machine failure"] == 0]
    X_healthy = healthy[FEATURES]

    pipe = build_pipeline()
    pipe.fit(X_healthy)

    # score_samples: higher means more normal, lower means more anomalous.
    healthy_scores = pipe.score_samples(X_healthy)
    threshold = float(np.percentile(healthy_scores, HEALTHY_PERCENTILE))

    # Sanity check: the detector never saw failures, so a higher flag rate on real
    # failures than on healthy readings is the signal that it generalizes.
    all_scores = pipe.score_samples(df[FEATURES])
    is_anom = all_scores < threshold
    failures = (df["Machine failure"] == 1).to_numpy()
    healthy_mask = ~failures

    print(f"rows: {len(df)}  healthy: {healthy_mask.sum()}  failures: {failures.sum()}")
    print(f"threshold (score_samples @ {HEALTHY_PERCENTILE:.0f}th pct): {threshold:.4f}")
    print(f"healthy flagged as anomaly:  {is_anom[healthy_mask].mean()*100:5.1f}%")
    print(f"failures flagged as anomaly: {is_anom[failures].mean()*100:5.1f}%")

    # Threshold sweep: healthy flag rate is your false-alarm cost, failure flag rate
    # is how much of the labeled trouble it happens to catch on its own. Pick the
    # HEALTHY_PERCENTILE constant that gives the tradeoff you want, then rerun.
    print("\n  pctile   threshold   healthy_flagged   failures_flagged")
    for pct in (1, 2, 5, 10):
        t = float(np.percentile(healthy_scores, pct))
        flag = all_scores < t
        print(f"  {pct:5d}    {t:8.4f}        {flag[healthy_mask].mean()*100:5.1f}%            {flag[failures].mean()*100:5.1f}%")

    bundle = {
        "model": pipe,
        "threshold": threshold,
        "features": FEATURES,
        "categorical": CATEGORICAL,
        "model_version": MODEL_VERSION,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
