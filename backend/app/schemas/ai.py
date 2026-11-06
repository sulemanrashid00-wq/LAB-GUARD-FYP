from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict


class AiInferenceRequest(BaseModel):
    lab_id: int
    device_id: Optional[int] = None
    inference_type: str = "anomaly_detection"  # anomaly_detection, fire_hazard_prediction, occupancy_forecast
    current_telemetry: Dict[str, Any]


class AiInferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    lab_id: int
    device_id: Optional[int] = None
    model_name: str
    model_version: str
    inference_type: str
    confidence_score: float
    is_anomaly: bool
    risk_level: str  # low, medium, high, critical
    prediction_output_json: Dict[str, Any]
    created_at: Optional[datetime] = None


class AnomalyReport(BaseModel):
    total_samples_analyzed: int
    anomalies_detected: int
    average_hazard_score: float
    high_risk_labs: List[str]
    recent_anomalies: List[AiInferenceResponse]

