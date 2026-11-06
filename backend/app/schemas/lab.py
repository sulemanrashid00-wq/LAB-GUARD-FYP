from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class LabBase(BaseModel):
    name: str
    code: str
    building: str
    room_number: str
    description: Optional[str] = None
    capacity: int = 30
    is_active: bool = True


class LabCreate(LabBase):
    pass


class LabUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    building: Optional[str] = None
    room_number: Optional[str] = None
    description: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class LabResponse(LabBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

