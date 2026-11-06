from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from app.models.command import DeviceCommand
from app.models.device import Device
from app.schemas.command import CommandCreate, CommandStatusUpdate
from app.core.errors import NotFoundError


class CommandService:
    @staticmethod
    def issue_command(db: Session, data: CommandCreate, user_id: Optional[Any] = None) -> DeviceCommand:
        device = db.query(Device).filter(Device.id == data.device_id).first()
        if not device:
            raise NotFoundError("Device", data.device_id)

        command = DeviceCommand(
            device_id=data.device_id,
            issued_by_id=user_id,
            command_type=data.command_type,
            payload_json=data.payload_json or {},
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        db.add(command)
        db.commit()
        db.refresh(command)
        return command

    @staticmethod
    def get_device_commands(db: Session, device_id: Any, status: Optional[str] = None) -> List[DeviceCommand]:
        query = db.query(DeviceCommand).filter(DeviceCommand.device_id == device_id)
        if status:
            query = query.filter(DeviceCommand.status == status)
        return query.order_by(DeviceCommand.created_at.desc()).all()

    @staticmethod
    def get_pending_commands(db: Session, device_id: Any) -> List[DeviceCommand]:
        return (
            db.query(DeviceCommand)
            .filter(DeviceCommand.device_id == device_id, DeviceCommand.status == "pending")
            .order_by(DeviceCommand.created_at.asc())
            .all()
        )

    @staticmethod
    def update_command_status(db: Session, command_id: Any, data: CommandStatusUpdate) -> DeviceCommand:

        command = db.query(DeviceCommand).filter(DeviceCommand.id == command_id).first()
        if not command:
            raise NotFoundError("DeviceCommand", command_id)

        command.status = data.status
        if data.response_json:
            command.response_json = data.response_json
        if data.status in ["executed", "failed"]:
            command.executed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(command)
        return command


command_service = CommandService()

