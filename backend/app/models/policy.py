from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Policy(Base, TimestampMixin):
    """
    Policy encapsulates dynamic laboratory safety rules, operational threshold constraints,
    and automatic remediation actions (e.g., if temp > 50C -> sound buzzer & raise critical alert).
    """
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    rule_type = Column(String(50), nullable=False)  # temperature_limit, gas_limit, after_hours_motion, sound_limit
    condition_operator = Column(String(10), default=">", nullable=False)  # >, <, >=, <=, ==
    threshold_value = Column(Float, nullable=False)
    action_type = Column(String(50), default="raise_alert", nullable=False)  # raise_alert, trigger_buzzer, cut_power, notify_admin
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    lab = relationship("Lab", back_populates="policies")

