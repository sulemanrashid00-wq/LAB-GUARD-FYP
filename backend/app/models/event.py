from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Event(Base):
    """
    Event captures distinct environmental or security incidents (e.g. motion detected after hours,
    gas threshold exceeded, door breached, unauthorized access attempt).
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # motion, gas_breach, temp_critical, lock_forced
    severity = Column(String(20), default="info", nullable=False)  # info, low, medium, high, critical
    description = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    lab = relationship("Lab", back_populates="events")
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")

