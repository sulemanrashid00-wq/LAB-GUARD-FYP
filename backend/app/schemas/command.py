from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class CommandBase(BaseModel):
    device_id: Any
    command_type: str  # reboot, lock_door, unlock_door, trigger_buzzer, cut_relay
    payload_json: Optional[Dict[str, Any]] = None


class CommandCreate(CommandBase):
    pass


class CommandStatusUpdate(BaseModel):
    status: str  # sent, acknowledged, executed, failed
    response_json: Optional[Dict[str, Any]] = None


class CommandResponse(CommandBase):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    issued_by_id: Optional[Any] = None
    status: str
    response_json: Optional[Dict[str, Any]] = None
    executed_at: Optional[datetime] = None
    created_at: datetime


