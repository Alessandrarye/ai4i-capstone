from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Reading
from ..schemas import ReadingIn, ReadingOut
from ..ml.scorer import score_reading
from pydantic import BaseModel

router = APIRouter()


@router.post("/readings", response_model=ReadingOut)
def create_reading(payload: ReadingIn, db: Session = Depends(get_db)):
    data = payload.model_dump()
    result = score_reading(data)
    reading = Reading(**data, score=result["score"], status=result["status"])
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/readings", response_model=list[ReadingOut])
def list_readings(
    limit: int = 20,
    machine_type: str | None = None,
    exclude_type: str | None = None,
    db: Session = Depends(get_db),
):
    q = select(Reading)
    if machine_type:
        q = q.where(Reading.machine_type == machine_type)
    if exclude_type:
        q = q.where(Reading.machine_type != exclude_type)
    rows = db.scalars(q.order_by(Reading.id.desc()).limit(limit)).all()
    return rows

# Live sensor rig (ESP32 vibration). The accelerometer does not produce the
# AI4I model's features, so this path scores vibration against a baseline
# threshold directly instead of calling the classifier. This is the anomaly
# idea applied to real hardware: quiet is normal, a spike is a fault.
VIBRATION_WARN = 0.07
VIBRATION_ALARM = 0.12


class LiveReadingIn(BaseModel):
    machine_id: str = "FAN"
    vibration: float


@router.post("/live-reading", response_model=ReadingOut)
def create_live_reading(payload: LiveReadingIn, db: Session = Depends(get_db)):
    v = payload.vibration
    if v >= VIBRATION_ALARM:
        status = "red"
    elif v >= VIBRATION_WARN:
        status = "yellow"
    else:
        status = "green"

    reading = Reading(
        machine_type=payload.machine_id,
        air_temp_k=0.0,
        process_temp_k=0.0,
        rotational_speed_rpm=0.0,
        torque_nm=0.0,
        tool_wear_min=0.0,
        score=v,
        status=status,
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading
