from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class AiInference(Base):
    """
    AiInference captures machine learning model inferences, predictive safety analysis,
    statistical anomaly detection, hazard likelihood scores, and occupancy counting.
    """
    __tablename__ = "ai_inferences"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id", ondelete="CASCADE"), nullable=False, index=True)
    model_name = Column(String(100), default="IsolationForest-EnvAnomaly", nullable=False)
    model_version = Column(String(30), default="v1.0", nullable=False)
    inference_type = Column(String(50), nullable=False)  # anomaly_detection, fire_hazard_prediction, occupancy_forecast
    confidence_score = Column(Float, nullable=False)     # 0.0 to 1.0
    is_anomaly = Column(Boolean, default=False, nullable=False, index=True)
    prediction_output_json = Column(JSON, default=dict, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    lab = relationship("Lab", back_populates="ai_inferences")

