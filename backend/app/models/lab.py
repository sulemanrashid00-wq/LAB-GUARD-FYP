from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Lab(Base, TimestampMixin):
    """
    Lab entity representing physical laboratory rooms, zones, and research facilities.
    """
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    code = Column(String(30), unique=True, index=True, nullable=False)  # e.g., LAB-CS-101
    building = Column(String(100), nullable=False)
    room_number = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    capacity = Column(Integer, default=30, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    events = relationship("Event", back_populates="lab", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="lab", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="lab", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="lab")
    ai_inferences = relationship("AiInference", back_populates="lab")

