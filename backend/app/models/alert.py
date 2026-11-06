from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Alert(Base):
    """
    Alert represents actionable safety or security incident notifications requiring
    operator intervention, triage, acknowledgment, or resolution.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    status = Column(String(30), default="active", nullable=False)    # active, acknowledged, resolved, dismissed
    acknowledged_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    lab = relationship("Lab", back_populates="alerts")
    event = relationship("Event", back_populates="alerts")
    acknowledged_by = relationship("User", foreign_keys=[acknowledged_by_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])

