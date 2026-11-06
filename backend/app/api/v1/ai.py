from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.ai import AiInferenceRequest, AiInferenceResponse, AnomalyReport
from app.schemas.common import APIResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI & Predictive Safety Analytics"])


@router.post("/inference", response_model=APIResponse[AiInferenceResponse], status_code=status.HTTP_200_OK)
def run_ai_inference(
    request: AiInferenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run predictive anomaly detection and hazard scoring against live or simulated telemetry data.
    """
    inference_result = ai_service.run_inference(db, request)
    return APIResponse(message="AI inference completed", data=inference_result)


@router.get("/anomalies", response_model=APIResponse[AnomalyReport])
def get_anomaly_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve laboratory hazard anomaly overview, risk distribution, and flagged incidents.
    """
    report = ai_service.get_anomaly_report(db)
    return APIResponse(data=report)


@router.get("/models", response_model=APIResponse[List[Dict[str, Any]]])
def list_ai_models(current_user: User = Depends(get_current_user)):
    """
    List registered machine learning models for anomaly detection and environmental hazard tracking.
    """
    models = [
        {
            "name": "LabGuard-Ensemble-AnomalyDetector",
            "version": "v1.0",
            "type": "Multi-Sensor Anomaly & Hazard Scorer",
            "status": "active",
            "features": ["temperature", "humidity", "gas_ppm", "smoke", "flame", "sound"],
            "accuracy": 0.942
        },
        {
            "name": "LabGuard-FireHazard-Predictor",
            "version": "v1.2",
            "type": "Early Stage Thermal Runaway & Fire Hazard",
            "status": "active",
            "features": ["temperature_rate_of_change", "gas_derivative", "smoke_detected"],
            "accuracy": 0.968
        }
    ]
    return APIResponse(data=models)

