from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class HealthData(BaseModel):
    cpu_pct: float
    ram_pct: float
    disk_used_pct: float
    disk_total_gb: float


class HeartbeatPayload(BaseModel):
    device_id: str
    timestamp: datetime
    agent_version: str
    agent_status: str
    health: Optional[HealthData] = None


class TelemetryBase(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    gas_ppm: Optional[float] = None
    smoke_detected: bool = False
    flame_detected: bool = False
    motion_detected: bool = False
    power_watts: Optional[float] = None
    sound_db: Optional[float] = None
    raw_data: Optional[Dict[str, Any]] = None


class TelemetryCreate(TelemetryBase):
    device_id: Any


class TelemetryResponse(TelemetryBase):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    device_id: Any
    recorded_at: Optional[datetime] = None


class TelemetryBatchCreate(BaseModel):
    device_id: Any
    readings: List[TelemetryBase]



class TelemetrySummary(BaseModel):
    avg_temperature: Optional[float] = None
    avg_humidity: Optional[float] = None
    max_gas_ppm: Optional[float] = None
    total_motion_triggers: int = 0
    readings_count: int = 0
