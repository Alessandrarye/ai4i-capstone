from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReadingIn(BaseModel):
    machine_type: str
    air_temp_k: float
    process_temp_k: float
    rotational_speed_rpm: float
    torque_nm: float
    tool_wear_min: float


class ReadingOut(ReadingIn):
    id: int
    created_at: datetime
    score: float | None = None
    status: str | None = None

    model_config = ConfigDict(from_attributes=True)
