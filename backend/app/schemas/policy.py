from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PolicyBase(BaseModel):
    lab_id: int
    name: str
    description: Optional[str] = None
    rule_type: str  # temperature_limit, gas_limit, after_hours_motion, sound_limit
    condition_operator: str = ">"  # >, <, >=, <=, ==
    threshold_value: float
    action_type: str = "raise_alert"  # raise_alert, trigger_buzzer, cut_power, notify_admin
    is_active: bool = True


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rule_type: Optional[str] = None
    condition_operator: Optional[str] = None
    threshold_value: Optional[float] = None
    action_type: Optional[str] = None
    is_active: Optional[bool] = None


class PolicyResponse(PolicyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

