import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class HeartbeatModel(Base):
    __tablename__ = "heartbeats"
    
    # UUID aur indexing for faster queries
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    # Foreign key directly linked to devices table
    device_id = Column(String, ForeignKey("devices.device_id", ondelete="CASCADE"), index=True, nullable=False)
    ts = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    agent_status = Column(String, default="running")
    agent_version = Column(String, nullable=True)

class TelemetryModel(Base):
    __tablename__ = "telemetry"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String, ForeignKey("devices.device_id", ondelete="CASCADE"), index=True, nullable=False)
    ts = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Hardware metrics
    cpu_pct = Column(Float, nullable=True)
    ram_pct = Column(Float, nullable=True)
    disk_used_pct = Column(Float, nullable=True)
    disk_total_gb = Column(Float, nullable=True)
    extra = Column(JSON, nullable=True)

    # Environmental & hardware sensor metrics
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    gas_ppm = Column(Float, nullable=True)
    smoke_detected = Column(Boolean, default=False)
    flame_detected = Column(Boolean, default=False)
    motion_detected = Column(Boolean, default=False)
    power_watts = Column(Float, nullable=True)
    sound_db = Column(Float, nullable=True)
    raw_data = Column(JSON, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


# Alias for backward compatibility
Telemetry = TelemetryModel

