from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.device import DeviceModel
from app.models.telemetry import HeartbeatModel, TelemetryModel
from app.schemas.telemetry import (
    HeartbeatPayload,
    TelemetryCreate,
    TelemetryResponse,
    TelemetrySummary,
)
from app.schemas.common import APIResponse
from app.services.telemetry_service import telemetry_service

router = APIRouter()
telemetry_router = APIRouter()


@router.post("/heartbeat", status_code=status.HTTP_201_CREATED)
def receive_heartbeat(payload: HeartbeatPayload, db: Session = Depends(get_db)):
    # 1. Check karein ke device registered hai ya nahi
    device = db.query(DeviceModel).filter(
        (DeviceModel.device_id == payload.device_id) | (DeviceModel.id == payload.device_id)
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device is not registered yet.")

    try:
        # 2. Device ka status aur last_seen real-time update karein
        device.last_seen = func.now()
        device.status = "online"
        device.agent_version = payload.agent_version

        # 3. Heartbeat history mein log add karein
        heartbeat = HeartbeatModel(
            device_id=payload.device_id,
            ts=payload.timestamp,
            agent_status=payload.agent_status,
            agent_version=payload.agent_version
        )
        db.add(heartbeat)

        # 4. Agar payload mein hardware health (CPU/RAM) hai, toh Telemetry table mein save karein
        if payload.health:
            telemetry = TelemetryModel(
                device_id=payload.device_id,
                ts=payload.timestamp,
                cpu_pct=payload.health.cpu_pct,
                ram_pct=payload.health.ram_pct,
                disk_used_pct=payload.health.disk_used_pct,
                disk_total_gb=payload.health.disk_total_gb
            )
            db.add(telemetry)

        # 5. Ek hi transaction mein sab save karein (Optimized)
        db.commit()
        return {"success": True, "message": "Heartbeat and telemetry processed successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database transaction failed: {str(e)}")


# General / Hardware Telemetry Endpoints
@telemetry_router.post("", response_model=APIResponse[TelemetryResponse], status_code=status.HTTP_201_CREATED)
def submit_telemetry(
    data: TelemetryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = telemetry_service.ingest_telemetry(db, data)
    return APIResponse(message="Telemetry recorded successfully", data=record)


@telemetry_router.get("/device/{device_id}", response_model=APIResponse[List[TelemetryResponse]])
def get_device_telemetry(
    device_id: Union[str, int],
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = telemetry_service.get_device_telemetry(db, device_id, limit=limit, skip=skip)
    return APIResponse(data=records)


@telemetry_router.get("/device/{device_id}/latest", response_model=APIResponse[Optional[TelemetryResponse]])
def get_latest_device_telemetry(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = telemetry_service.get_latest_device_telemetry(db, device_id)
    return APIResponse(data=record)


@telemetry_router.get("/device/{device_id}/summary", response_model=APIResponse[TelemetrySummary])
def get_telemetry_summary(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    summary = telemetry_service.get_telemetry_summary(db, device_id)
    return APIResponse(data=summary)



# General / Hardware Telemetry Endpoints
@telemetry_router.post("", response_model=APIResponse[TelemetryResponse], status_code=status.HTTP_201_CREATED)
def submit_telemetry(
    data: TelemetryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = telemetry_service.ingest_telemetry(db, data)
    return APIResponse(message="Telemetry recorded successfully", data=record)


@telemetry_router.get("/device/{device_id}", response_model=APIResponse[List[TelemetryResponse]])
def get_device_telemetry(
    device_id: Union[str, int],
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = telemetry_service.get_device_telemetry(db, device_id, limit=limit, skip=skip)
    return APIResponse(data=records)


@telemetry_router.get("/device/{device_id}/latest", response_model=APIResponse[Optional[TelemetryResponse]])
def get_latest_device_telemetry(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = telemetry_service.get_latest_device_telemetry(db, device_id)
    return APIResponse(data=record)


@telemetry_router.get("/device/{device_id}/summary", response_model=APIResponse[TelemetrySummary])
def get_telemetry_summary(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    summary = telemetry_service.get_telemetry_summary(db, device_id)
    return APIResponse(data=summary)