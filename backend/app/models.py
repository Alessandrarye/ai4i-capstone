from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    machine_type: Mapped[str] = mapped_column(String(10))
    air_temp_k: Mapped[float] = mapped_column(Float)
    process_temp_k: Mapped[float] = mapped_column(Float)
    rotational_speed_rpm: Mapped[float] = mapped_column(Float)
    torque_nm: Mapped[float] = mapped_column(Float)
    tool_wear_min: Mapped[float] = mapped_column(Float)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str | None] = mapped_column(String(10), nullable=True)
