"""Replay the AI4I CSV through the ingestion API to simulate live sensors.

Usage (once the FastAPI backend is running):
    python scripts/replay.py --interval 3
Until then this is a stub that validates the CSV loads and prints what it
would send, so the demo script exists from day one and grows with the API.
"""
import argparse
import time
from pathlib import Path

import pandas as pd
import requests

API_URL = "http://localhost:8000/readings"
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "ai4i2020.csv"


def row_to_payload(row) -> dict:
    return {
        "machine_type": row["Type"],
        "air_temp_k": row["Air temperature [K]"],
        "process_temp_k": row["Process temperature [K]"],
        "rotational_speed_rpm": row["Rotational speed [rpm]"],
        "torque_nm": row["Torque [Nm]"],
        "tool_wear_min": row["Tool wear [min]"],
    }


def main(interval: float, dry_run: bool, limit: int | None):
    df = pd.read_csv(CSV_PATH)
    rows = df if limit is None else df.head(limit)
    for i, (_, row) in enumerate(rows.iterrows(), start=1):
        payload = row_to_payload(row)
        if dry_run:
            print(f"[{i}] would POST {payload}")
        else:
            try:
                r = requests.post(API_URL, json=payload, timeout=5)
                print(f"[{i}] {r.status_code} {r.json()}")
            except requests.ConnectionError:
                print(f"[{i}] API not reachable at {API_URL}; is the backend running?")
                return
        time.sleep(interval)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=float, default=3.0, help="seconds between readings")
    p.add_argument("--dry-run", action="store_true", help="print payloads without POSTing")
    p.add_argument("--limit", type=int, default=None, help="only send the first N rows")
    args = p.parse_args()
    main(args.interval, args.dry_run, args.limit)
