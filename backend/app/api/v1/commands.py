from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.command import CommandCreate, CommandResponse, CommandStatusUpdate
from app.schemas.common import APIResponse
from app.services.command_service import command_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/commands", tags=["Device Commands & Remote Actuation"])


@router.post("", response_model=APIResponse[CommandResponse], status_code=status.HTTP_201_CREATED)
def issue_device_command(
    command_in: CommandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dispatch a remote hardware command (reboot, lock_door, unlock_door, trigger_buzzer, cut_relay).
    """
    command = command_service.issue_command(db, command_in, user_id=current_user.id)
    audit_service.log_action(
        db,
        action="ISSUE_COMMAND",
        user_id=current_user.id,
        resource_type="device",
        resource_id=str(command.device_id),
        details={"command_type": command.command_type, "command_id": command.id}
    )
    return APIResponse(message="Command queued for device execution", data=command)


@router.get("/device/{device_id}", response_model=APIResponse[List[CommandResponse]])
def get_device_commands(
    device_id: int,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get command audit log and status history for a given device.
    """
    commands = command_service.get_device_commands(db, device_id=device_id, status=status_filter)
    return APIResponse(data=commands)


@router.patch("/{command_id}/status", response_model=APIResponse[CommandResponse])
def update_command_status(
    command_id: int,
    status_update: CommandStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update command status execution outcome (e.g., executed, failed).
    """
    cmd = command_service.update_command_status(db, command_id, status_update)
    return APIResponse(message=f"Command status updated to {cmd.status}", data=cmd)

