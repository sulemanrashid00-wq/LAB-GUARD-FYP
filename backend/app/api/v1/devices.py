from typing import List, Optional, Union
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_admin
from app.models.user import User
from app.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceRegisterRequest,
    DeviceRegisterResponse,
)
from app.schemas.common import APIResponse
from app.services.device_service import device_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/devices", tags=["Devices & Hardware"])


@router.get("", response_model=APIResponse[List[DeviceResponse]])
def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    lab_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all registered IoT nodes, environmental sensors, cameras, and smart controllers.
    """
    devices = device_service.get_devices(db, skip=skip, limit=limit, lab_id=lab_id)
    return APIResponse(data=devices)


@router.get("/{device_id}", response_model=APIResponse[DeviceResponse])
def get_device(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific device.
    """
    device = device_service.get_device_by_id(db, device_id)
    return APIResponse(data=device)


@router.post("/register", response_model=APIResponse[DeviceRegisterResponse], status_code=status.HTTP_201_CREATED)
def register_device_endpoint(
    device_in: DeviceRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Direct registration endpoint for LabGuard-X PC agents and monitored devices.
    Saves device credentials and initial state directly to the Supabase database.
    """
    device = device_service.register_agent_device(db, device_in)
    return APIResponse(message="Device registered successfully", data=device)


@router.post("", response_model=APIResponse[DeviceResponse], status_code=status.HTTP_201_CREATED)
def create_device(
    device_in: DeviceCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Register a new hardware device / sensor node into the system (Admin only).
    """
    device = device_service.create_device(db, device_in)
    audit_service.log_action(
        db,
        action="CREATE_DEVICE",
        user_id=current_admin.id,
        resource_type="device",
        resource_id=str(device.id),
        details={"name": device.name, "mac_address": device.mac_address}
    )
    return APIResponse(message="Device registered successfully", data=device)


@router.patch("/{device_id}", response_model=APIResponse[DeviceResponse])
def update_device(
    device_id: Union[str, int],
    device_in: DeviceUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Update device parameters, assignment, or status (Admin only).
    """
    device = device_service.update_device(db, device_id, device_in)
    audit_service.log_action(
        db,
        action="UPDATE_DEVICE",
        user_id=current_admin.id,
        resource_type="device",
        resource_id=str(device.id),
        details=device_in.model_dump(exclude_unset=True)
    )
    return APIResponse(message="Device updated successfully", data=device)


@router.delete("/{device_id}", response_model=APIResponse[dict])
def delete_device(
    device_id: Union[str, int],
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):

    """
    Remove a hardware device from the registry (Admin only).
    """
    device_service.delete_device(db, device_id)
    audit_service.log_action(
        db,
        action="DELETE_DEVICE",
        user_id=current_admin.id,
        resource_type="device",
        resource_id=str(device_id)
    )
    return APIResponse(message="Device deleted successfully", data={"deleted_id": device_id})

