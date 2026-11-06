from typing import List, Optional, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.telemetry import Telemetry
from app.models.device import Device
from app.schemas.telemetry import TelemetryCreate, TelemetrySummary
from app.core.errors import NotFoundError


class TelemetryService:
    @staticmethod
    def ingest_telemetry(db: Session, data: TelemetryCreate) -> Telemetry:
        # Validate device
        device = db.query(Device).filter(Device.id == data.device_id).first()
        if not device:
            raise NotFoundError("Device", data.device_id)

        telemetry = Telemetry(
            device_id=data.device_id,
            temperature=data.temperature,
            humidity=data.humidity,
            gas_ppm=data.gas_ppm,
            smoke_detected=data.smoke_detected,
            flame_detected=data.flame_detected,
            motion_detected=data.motion_detected,
            power_watts=data.power_watts,
            sound_db=data.sound_db,
            raw_data=data.raw_data or {},
            recorded_at=datetime.now(timezone.utc)
        )
        db.add(telemetry)

        # Update device heartbeat & status
        device.last_heartbeat = datetime.now(timezone.utc)
        device.status = "online"

        db.commit()
        db.refresh(telemetry)
        return telemetry

    @staticmethod
    def get_device_telemetry(
        db: Session,
        device_id: Any,
        limit: int = 50,
        skip: int = 0
    ) -> List[Telemetry]:
        return (
            db.query(Telemetry)
            .filter(Telemetry.device_id == device_id)
            .order_by(Telemetry.recorded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_latest_device_telemetry(db: Session, device_id: Any) -> Optional[Telemetry]:
        return (
            db.query(Telemetry)
            .filter(Telemetry.device_id == device_id)
            .order_by(Telemetry.recorded_at.desc())
            .first()
        )

    @staticmethod
    def get_telemetry_summary(db: Session, device_id: Any) -> TelemetrySummary:
        records = db.query(Telemetry).filter(Telemetry.device_id == device_id).all()
        if not records:
            return TelemetrySummary()

        temps = [r.temperature for r in records if r.temperature is not None]
        humids = [r.humidity for r in records if r.humidity is not None]
        gases = [r.gas_ppm for r in records if r.gas_ppm is not None]
        motion_count = sum(1 for r in records if r.motion_detected)

        return TelemetrySummary(
            avg_temperature=round(sum(temps) / len(temps), 2) if temps else None,
            avg_humidity=round(sum(humids) / len(humids), 2) if humids else None,
            max_gas_ppm=max(gases) if gases else None,
            total_motion_triggers=motion_count,
            readings_count=len(records)
        )


telemetry_service = TelemetryService()

