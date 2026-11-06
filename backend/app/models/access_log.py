from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class AccessLog(Base):
    """
    AccessLog records all entry/exit authentication attempts to secure lab facilities
    via RFID badges, PIN keypads, biometric scanners, or remote software triggers.
    """
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    access_method = Column(String(50), default="rfid", nullable=False)   # rfid, pin, biometric, mobile_app, manual_override
    access_status = Column(String(30), default="granted", nullable=False) # granted, denied, expired, unauthorized
    card_uid = Column(String(50), nullable=True)
    reason = Column(String(255), nullable=True)
    accessed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    lab = relationship("Lab", back_populates="access_logs")
    user = relationship("User")

