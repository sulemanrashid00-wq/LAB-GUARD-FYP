import uuid
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class DeviceModel(Base):
    """
    DeviceModel representing lab PCs and monitored nodes (Supabase ERD v0).
    """
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String, unique=True, index=True, nullable=True)  # e.g., PC-001
    hostname = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    os = Column(String, nullable=True)
    agent_version = Column(String, nullable=True)
    status = Column(String, default="offline")  # online, stale, offline
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    # Sensor and compatibility columns
    name = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    mac_address = Column(String, nullable=True, index=True)
    lab_id = Column(Integer, nullable=True)
    ip_address = Column(String, nullable=True)
    firmware_version = Column(String, nullable=True, default="1.0.0")
    api_key = Column(String, nullable=True)

    def __init__(self, **kwargs):
        if "device_id" not in kwargs:
            kwargs["device_id"] = kwargs.get("mac_address") or str(uuid.uuid4())
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        super().__init__(**kwargs)


# Alias for backward compatibility
Device = DeviceModel

