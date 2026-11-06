from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from app.schemas.common import APIResponse
from app.services.alert_service import alert_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/alerts", tags=["Alerts & Notifications"])


@router.get("", response_model=APIResponse[List[AlertResponse]])
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: Optional[str] = Query(None, alias="status"),
    lab_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List alerts filtered by status (active, acknowledged, resolved) or lab.
    """
    alerts = alert_service.get_alerts(db, skip=skip, limit=limit, status_filter=status_filter, lab_id=lab_id)
    return APIResponse(data=alerts)


@router.get("/{alert_id}", response_model=APIResponse[AlertResponse])
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch details of a specific alert.
    """
    alert = alert_service.get_alert_by_id(db, alert_id)
    return APIResponse(data=alert)


@router.post("", response_model=APIResponse[AlertResponse], status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_in: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually raise a critical lab security or safety alert.
    """
    alert = alert_service.create_alert(db, alert_in)
    audit_service.log_action(
        db,
        action="MANUAL_ALERT_RAISED",
        user_id=current_user.id,
        resource_type="alert",
        resource_id=str(alert.id),
        details={"title": alert.title, "severity": alert.severity}
    )
    return APIResponse(message="Alert created", data=alert)


@router.patch("/{alert_id}", response_model=APIResponse[AlertResponse])
def update_alert_status(
    alert_id: int,
    alert_in: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update alert state: acknowledge or resolve the alert.
    """
    alert = alert_service.update_alert(db, alert_id, alert_in, current_user_id=current_user.id)
    audit_service.log_action(
        db,
        action=f"ALERT_{alert.status.upper()}",
        user_id=current_user.id,
        resource_type="alert",
        resource_id=str(alert.id),
        details={"status": alert.status}
    )
    return APIResponse(message=f"Alert marked as {alert.status}", data=alert)

