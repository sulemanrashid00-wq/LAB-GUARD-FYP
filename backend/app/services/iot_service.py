from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.telemetry import Telemetry
from app.models.command import DeviceCommand
from app.schemas.iot import IoTHeartbeat, IoTTelemetryIngest, IoTCommandAck, IoTRegisterRequest
from app.services.telemetry_service import telemetry_service
from app.services.policy_service import policy_service
from app.core.errors import NotFoundError, ConflictError


class IoTService:
    @staticmethod
    def register_iot_device(db: Session, req: IoTRegisterRequest) -> Device:
        existing = db.query(Device).filter(Device.mac_address == req.mac_address).first()
        if existing:
            return existing

        device = Device(
            name=req.name,
            device_type=req.device_type,
            mac_address=req.mac_address,
            lab_id=req.lab_id,
            firmware_version=req.firmware_version or "1.0.0",
            status="online",
            last_heartbeat=datetime.now(timezone.utc)
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def process_heartbeat(db: Session, heartbeat: IoTHeartbeat) -> Dict[str, Any]:
        device = db.query(Device).filter(Device.mac_address == heartbeat.mac_address).first()
        if not device and heartbeat.device_id:
            device = db.query(Device).filter(Device.id == heartbeat.device_id).first()

        if not device:
            raise NotFoundError("Device", heartbeat.mac_address)

        device.last_heartbeat = datetime.now(timezone.utc)
        device.status = "online"
        if heartbeat.ip_address:
            device.ip_address = heartbeat.ip_address
        if heartbeat.firmware_version:
            device.firmware_version = heartbeat.firmware_version

        db.commit()
        db.refresh(device)

        # Check for pending commands to return to device
        pending_commands = (
            db.query(DeviceCommand)
            .filter(DeviceCommand.device_id == device.id, DeviceCommand.status == "pending")
            .all()
        )

        return {
            "status": "ok",
            "device_id": device.id,
            "server_time": datetime.now(timezone.utc).isoformat(),
            "pending_commands_count": len(pending_commands),
            "pending_commands": [
                {"id": cmd.id, "type": cmd.command_type, "payload": cmd.payload_json}
                for cmd in pending_commands
            ]
        }

    @staticmethod
    def ingest_iot_telemetry(db: Session, payload: IoTTelemetryIngest, authenticated_device_id: Optional[int] = None) -> Telemetry:
        target_device_id = authenticated_device_id or payload.device_id
        if not target_device_id and payload.device_mac:
            dev = db.query(Device).filter(Device.mac_address == payload.device_mac).first()
            if dev:
                target_device_id = dev.id

        if not target_device_id:
            raise NotFoundError("Device", "Unknown device reference")

        device = db.query(Device).filter(Device.id == target_device_id).first()
        if not device:
            raise NotFoundError("Device", target_device_id)

        telemetry = Telemetry(
            device_id=device.id,
            temperature=payload.temperature,
            humidity=payload.humidity,
            gas_ppm=payload.gas_ppm,
            smoke_detected=payload.smoke_detected,
            flame_detected=payload.flame_detected,
            motion_detected=payload.motion_detected,
            power_watts=payload.power_watts,
            sound_db=payload.sound_db,
            raw_data=payload.raw_data or {},
            recorded_at=datetime.now(timezone.utc)
        )
        db.add(telemetry)
        device.last_heartbeat = datetime.now(timezone.utc)
        device.status = "online"
        db.commit()
        db.refresh(telemetry)

        # Evaluate against safety policies if device belongs to a lab
        if device.lab_id:
            policy_service.evaluate_telemetry(db, telemetry, device.lab_id)

        return telemetry

    @staticmethod
    def acknowledge_command(db: Session, ack: IoTCommandAck) -> DeviceCommand:
        cmd = db.query(DeviceCommand).filter(DeviceCommand.id == ack.command_id).first()
        if not cmd:
            raise NotFoundError("DeviceCommand", ack.command_id)

        cmd.status = ack.status
        cmd.response_json = {"message": ack.result_message, "details": ack.details or {}}
        cmd.executed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(cmd)
        return cmd


iot_service = IoTService()

