from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class DeviceConfig(Base, TimestampMixin):
    """
    DeviceConfig holds hardware parameters, sampling rates, reporting intervals,
    and custom sensor sensitivity calibration payloads for each IoT device.
    """
    __tablename__ = "device_configs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), unique=True, nullable=False)
    sampling_rate_sec = Column(Integer, default=5, nullable=False)
    reporting_interval_sec = Column(Integer, default=30, nullable=False)
    sensitivity = Column(String(20), default="medium", nullable=False)  # low, medium, high
    sleep_mode_enabled = Column(Boolean, default=False, nullable=False)
    config_json = Column(JSON, default=dict, nullable=False)

    # Relationship
    pass

