from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.schemas.telemetry import TelemetryBase


class IoTHeartbeat(BaseModel):
    device_id: Optional[int] = None
    mac_address: str
    ip_address: Optional[str] = None
    firmware_version: Optional[str] = None
    battery_level: Optional[float] = None
    wifi_rssi: Optional[int] = None


class IoTTelemetryIngest(TelemetryBase):
    device_mac: Optional[str] = None
    device_id: Optional[int] = None


class IoTCommandAck(BaseModel):
    command_id: int
    status: str  # acknowledged, executed, failed
    result_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class IoTRegisterRequest(BaseModel):
    name: str
    device_type: str
    mac_address: str
    lab_id: Optional[int] = None
    firmware_version: Optional[str] = "1.0.0"


class IoTRegisterResponse(BaseModel):
    device_id: int
    name: str
    api_key: str
    mac_address: str
    status: str
    message: str = "Device registered successfully. Keep API key secure."

