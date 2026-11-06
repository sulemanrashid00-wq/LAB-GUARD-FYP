from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    lab_id: int
    device_id: Optional[Any] = None
    event_type: str
    severity: str = "info"  # info, low, medium, high, critical
    description: str
    metadata_json: Optional[Dict[str, Any]] = None


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    created_at: datetime


