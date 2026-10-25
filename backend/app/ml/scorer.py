"""Load the trained model bundle and score a single reading."""
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# models/ lives at the repo root, three parents up from this file
MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "failure_model_v0.1.joblib"

_bundle = joblib.load(MODEL_PATH)
_model = _bundle["model"]
_threshold = _bundle["threshold"]
_features = _bundle["features"]
_version = _bundle.get("model_version", "unknown")

# the anomaly detector sits beside the classifier in models/
ANOM_PATH = Path(__file__).resolve().parents[3] / "models" / "anomaly_model_v0.1.joblib"
_anom_bundle = joblib.load(ANOM_PATH)
_anom_model = _anom_bundle["model"]
_anom_threshold = _anom_bundle["threshold"]

# Warn (yellow) band: a fraction of the fail threshold flags "getting close"
_WARN_FRACTION = 0.5


def _build_row(reading: dict) -> pd.DataFrame:
    """Turn an API reading into the one-row frame the model expects."""
    air = reading["air_temp_k"]
    process = reading["process_temp_k"]
    rpm = reading["rotational_speed_rpm"]
    torque = reading["torque_nm"]

    row = {
        "Type": reading["machine_type"],
        "Air temperature [K]": air,
        "Process temperature [K]": process,
        "Rotational speed [rpm]": rpm,
        "Torque [Nm]": torque,
        "Tool wear [min]": reading["tool_wear_min"],
        "temp_delta": process - air,
        "power": torque * rpm * 2 * np.pi / 60,
    }
    return pd.DataFrame([row], columns=_features)


def score_reading(reading: dict) -> dict:
    """Return failure probability and a green/yellow/red status."""
    X = _build_row(reading)
    prob = float(_model.predict_proba(X)[0][1])

    # unsupervised detector: lower score means more abnormal
    anom_score = float(_anom_model.score_samples(X)[0])
    is_anomaly = anom_score < _anom_threshold

    if prob >= _threshold:
        status = "red"
    elif prob >= _threshold * _WARN_FRACTION:
        status = "yellow"
    else:
        status = "green"

    # the detector can raise an otherwise-healthy reading: a pattern the
    # classifier was never trained on still gets flagged for a look
    if is_anomaly and status == "green":
        status = "yellow"

    return {"score": prob, "status": status}


def model_info() -> dict:
    return {"model_version": _version, "threshold": _threshold, "features": _features}
