from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class DeviceConfigSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sampling_rate_sec: int = 5
    reporting_interval_sec: int = 30
    sensitivity: str = "medium"
    sleep_mode_enabled: bool = False
    config_json: Dict[str, Any] = {}


class DeviceBase(BaseModel):
    name: str
    device_type: str
    mac_address: str
    lab_id: Optional[int] = None
    ip_address: Optional[str] = None
    firmware_version: str = "1.0.0"


class DeviceCreate(DeviceBase):
    config: Optional[DeviceConfigSchema] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    lab_id: Optional[int] = None
    ip_address: Optional[str] = None
    status: Optional[str] = None
    firmware_version: Optional[str] = None


class DeviceResponse(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    status: str
    api_key: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    config: Optional[DeviceConfigSchema] = None


class DeviceRegisterRequest(BaseModel):
    device_id: str  # e.g., PC-001
    hostname: Optional[str] = None
    ip: Optional[str] = None
    os: Optional[str] = None
    agent_version: Optional[str] = "1.0.0"


class DeviceRegisterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str
    hostname: Optional[str] = None
    ip: Optional[str] = None
    os: Optional[str] = None
    agent_version: Optional[str] = None
    status: str = "online"
    registered_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None


