from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DeviceCommand(Base):
    """
    DeviceCommand records control instructions dispatched to IoT hardware devices
    (e.g., lock door, sound alarm buzzer, reboot microcontroller, trigger power relay).
    """
    __tablename__ = "device_commands"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    issued_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    command_type = Column(String(50), nullable=False)  # reboot, lock_door, unlock_door, trigger_buzzer, cut_relay
    payload_json = Column(JSON, default=dict, nullable=True)
    status = Column(String(30), default="pending", nullable=False)  # pending, sent, acknowledged, executed, failed
    response_json = Column(JSON, default=dict, nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    issuer = relationship("User")

