from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class AuditLog(Base):
    """
    AuditLog tracks sensitive security-critical events, administrator actions,
    policy changes, manual device overrides, and user authentication events.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # LOGIN, LOGOUT, CREATE_POLICY, OVERRIDE_LOCK, etc.
    resource_type = Column(String(50), nullable=True)         # device, policy, alert, user, lab
    resource_id = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    details_json = Column(JSON, default=dict, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    user = relationship("User")

