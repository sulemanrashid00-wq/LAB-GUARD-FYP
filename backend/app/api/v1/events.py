from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.event import EventCreate, EventResponse
from app.schemas.common import APIResponse
from app.services.event_service import event_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/events", tags=["Events & Incidents"])


@router.get("", response_model=APIResponse[List[EventResponse]])
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    lab_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Query logged lab events and environmental incident records.
    """
    events = event_service.get_events(db, skip=skip, limit=limit, lab_id=lab_id, severity=severity)
    return APIResponse(data=events)


@router.get("/{event_id}", response_model=APIResponse[EventResponse])
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve details of a single event.
    """
    event = event_service.get_event_by_id(db, event_id)
    return APIResponse(data=event)


@router.post("", response_model=APIResponse[EventResponse], status_code=status.HTTP_201_CREATED)
def create_manual_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a manual or externally triggered lab incident event.
    """
    event = event_service.create_event(db, event_in)
    audit_service.log_action(
        db,
        action="CREATE_EVENT",
        user_id=current_user.id,
        resource_type="event",
        resource_id=str(event.id),
        details={"type": event.event_type, "severity": event.severity}
    )
    return APIResponse(message="Event created", data=event)

