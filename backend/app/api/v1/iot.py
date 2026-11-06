from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_iot_api_key
from app.schemas.iot import (
    IoTHeartbeat,
    IoTTelemetryIngest,
    IoTCommandAck,
    IoTRegisterRequest,
    IoTRegisterResponse
)
from app.schemas.telemetry import TelemetryResponse
from app.schemas.command import CommandResponse
from app.schemas.common import APIResponse
from app.services.iot_service import iot_service
from app.services.command_service import command_service

router = APIRouter(prefix="/iot", tags=["IoT Hardware Gateway Interface"])


@router.post("/register", response_model=APIResponse[IoTRegisterResponse], status_code=status.HTTP_201_CREATED)
def register_iot_device(payload: IoTRegisterRequest, db: Session = Depends(get_db)):
    """
    Onboard and register physical IoT microcontrollers, sensors, or smart gateways.
    """
    device = iot_service.register_iot_device(db, payload)
    return APIResponse(
        message="Device successfully provisioned",
        data=IoTRegisterResponse(
            device_id=device.id,
            name=device.name,
            api_key=device.api_key,
            mac_address=device.mac_address,
            status=device.status
        )
    )


@router.post("/heartbeat", response_model=APIResponse[Dict[str, Any]])
def send_device_heartbeat(
    heartbeat: IoTHeartbeat,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Device keep-alive ping. Updates device online status and returns queued commands.
    """
    if not heartbeat.ip_address and request.client:
        heartbeat.ip_address = request.client.host

    result = iot_service.process_heartbeat(db, heartbeat)
    return APIResponse(message="Heartbeat processed", data=result)


@router.post("/telemetry", response_model=APIResponse[TelemetryResponse], status_code=status.HTTP_201_CREATED)
def submit_iot_sensor_data(
    payload: IoTTelemetryIngest,
    db: Session = Depends(get_db),
    auth_info: dict = Depends(verify_iot_api_key)
):
    """
    Hardware endpoint to ingest sensor packets using X-IoT-API-Key authentication.
    Automatically evaluates telemetry against lab safety policies.
    """
    authenticated_device_id = auth_info.get("device_id")
    telemetry = iot_service.ingest_iot_telemetry(db, payload, authenticated_device_id=authenticated_device_id)
    return APIResponse(message="Sensor telemetry recorded and analyzed", data=telemetry)


@router.get("/commands/pending", response_model=APIResponse[List[CommandResponse]])
def get_pending_device_commands(
    db: Session = Depends(get_db),
    auth_info: dict = Depends(verify_iot_api_key)
):
    """
    Poll pending commands queued for this specific authenticated device.
    """
    device_id = auth_info.get("device_id")
    if not device_id:
        return APIResponse(data=[])
    commands = command_service.get_pending_commands(db, device_id=device_id)
    return APIResponse(data=commands)


@router.post("/commands/ack", response_model=APIResponse[dict])
def acknowledge_command_execution(
    ack: IoTCommandAck,
    db: Session = Depends(get_db),
    auth_info: dict = Depends(verify_iot_api_key)
):
    """
    Hardware feedback loop: Device confirms execution of a remote instruction.
    """
    cmd = iot_service.acknowledge_command(db, ack)
    return APIResponse(message="Command execution confirmed", data={"command_id": cmd.id, "status": cmd.status})

