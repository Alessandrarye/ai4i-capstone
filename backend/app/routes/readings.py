from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Reading
from ..schemas import ReadingIn, ReadingOut

router = APIRouter()


@router.post("/readings", response_model=ReadingOut)
def create_reading(payload: ReadingIn, db: Session = Depends(get_db)):
    reading = Reading(**payload.model_dump())
    # Model scoring gets added in pass two; score/status stay empty for now.
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("/readings", response_model=list[ReadingOut])
def list_readings(limit: int = 20, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Reading).order_by(Reading.id.desc()).limit(limit)
    ).all()
    return rows
