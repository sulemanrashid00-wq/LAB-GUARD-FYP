from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import math
from sqlalchemy.orm import Session
from app.models.ai_inference import AiInference
from app.models.telemetry import Telemetry
from app.models.lab import Lab
from app.schemas.ai import AiInferenceRequest, AiInferenceResponse, AnomalyReport
from app.core.config import settings
from app.core.errors import NotFoundError


class AiService:
    """
    AI Service for intelligent lab safety: Anomaly detection, multi-sensor hazard scoring,
    and predictive risk classification.
    """

    @staticmethod
    def calculate_hazard_score(telemetry_data: Dict[str, Any]) -> float:
        """
        Heuristic / ML proxy scoring for lab hazards:
        Combines temperature, gas PPM, smoke, and flame presence into a normalized 0.0 - 1.0 risk score.
        """
        score = 0.0
        temp = telemetry_data.get("temperature", 22.0) or 22.0
        gas = telemetry_data.get("gas_ppm", 100.0) or 100.0
        smoke = bool(telemetry_data.get("smoke_detected", False))
        flame = bool(telemetry_data.get("flame_detected", False))

        # Temperature risk contribution (>40 C starts scaling)
        if temp > 40:
            score += min(0.35, (temp - 40) / 40.0 * 0.35)

        # Gas PPM risk contribution (>300 ppm starts scaling)
        if gas > 300:
            score += min(0.35, (gas - 300) / 700.0 * 0.35)

        # Binary sensor multipliers
        if smoke:
            score += 0.30
        if flame:
            score += 0.40

        return round(min(1.0, score), 3)

    @staticmethod
    def run_inference(db: Session, request: AiInferenceRequest) -> AiInferenceResponse:
        lab = db.query(Lab).filter(Lab.id == request.lab_id).first()
        if not lab:
            raise NotFoundError("Lab", request.lab_id)

        hazard_score = AiService.calculate_hazard_score(request.current_telemetry)
        is_anomaly = hazard_score >= settings.AI_ANOMALY_THRESHOLD

        if hazard_score >= 0.85:
            risk_level = "critical"
        elif hazard_score >= 0.60:
            risk_level = "high"
        elif hazard_score >= 0.30:
            risk_level = "medium"
        else:
            risk_level = "low"

        prediction_details = {
            "hazard_score": hazard_score,
            "anomaly_detected": is_anomaly,
            "evaluated_features": request.current_telemetry,
            "recommended_actions": (
                ["Trigger Fire Suppression", "Evacuate Lab", "Notify Fire Marshall"]
                if risk_level in ["high", "critical"]
                else ["Routine Monitoring"]
            )
        }

        # Persist record in ai_inferences table
        inference_record = AiInference(
            device_id=request.device_id,
            lab_id=request.lab_id,
            model_name="LabGuard-Ensemble-AnomalyDetector",
            model_version="v1.0",
            inference_type=request.inference_type,
            confidence_score=hazard_score,
            is_anomaly=is_anomaly,
            prediction_output_json=prediction_details,
            created_at=datetime.now(timezone.utc)
        )
        db.add(inference_record)
        db.commit()
        db.refresh(inference_record)

        return AiInferenceResponse(
            id=inference_record.id,
            lab_id=inference_record.lab_id,
            device_id=inference_record.device_id,
            model_name=inference_record.model_name,
            model_version=inference_record.model_version,
            inference_type=inference_record.inference_type,
            confidence_score=inference_record.confidence_score,
            is_anomaly=inference_record.is_anomaly,
            risk_level=risk_level,
            prediction_output_json=inference_record.prediction_output_json,
            created_at=inference_record.created_at
        )

    @staticmethod
    def get_anomaly_report(db: Session) -> AnomalyReport:
        inferences = db.query(AiInference).order_by(AiInference.created_at.desc()).limit(100).all()
        total_samples = len(inferences)
        anomalies = [inf for inf in inferences if inf.is_anomaly]

        avg_score = (
            sum(inf.confidence_score for inf in inferences) / total_samples
            if total_samples > 0
            else 0.0
        )

        high_risk_lab_ids = list({inf.lab_id for inf in anomalies})
        high_risk_labs = [f"Lab-{lid}" for lid in high_risk_lab_ids]

        recent_anomalies_resp = [
            AiInferenceResponse(
                id=inf.id,
                lab_id=inf.lab_id,
                device_id=inf.device_id,
                model_name=inf.model_name,
                model_version=inf.model_version,
                inference_type=inf.inference_type,
                confidence_score=inf.confidence_score,
                is_anomaly=inf.is_anomaly,
                risk_level="high" if inf.confidence_score > 0.6 else "medium",
                prediction_output_json=inf.prediction_output_json,
                created_at=inf.created_at
            )
            for inf in anomalies[:10]
        ]

        return AnomalyReport(
            total_samples_analyzed=total_samples,
            anomalies_detected=len(anomalies),
            average_hazard_score=round(avg_score, 3),
            high_risk_labs=high_risk_labs,
            recent_anomalies=recent_anomalies_resp
        )


ai_service = AiService()

