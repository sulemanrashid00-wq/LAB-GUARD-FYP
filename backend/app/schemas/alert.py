from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    lab_id: int
    event_id: Optional[int] = None
    title: str
    description: str
    severity: str = "medium"


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[str] = None  # acknowledged, resolved, dismissed
    acknowledged_by_id: Optional[int] = None
    resolved_by_id: Optional[int] = None


class AlertResponse(AlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    acknowledged_by_id: Optional[int] = None
    resolved_by_id: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

