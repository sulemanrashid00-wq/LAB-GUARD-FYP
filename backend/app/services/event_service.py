from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.event import Event
from app.schemas.event import EventCreate
from app.core.errors import NotFoundError


class EventService:
    @staticmethod
    def create_event(db: Session, data: EventCreate) -> Event:
        event = Event(
            lab_id=data.lab_id,
            device_id=data.device_id,
            event_type=data.event_type,
            severity=data.severity,
            description=data.description,
            metadata_json=data.metadata_json or {},
            created_at=datetime.now(timezone.utc)
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def get_events(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        lab_id: Optional[int] = None,
        severity: Optional[str] = None
    ) -> List[Event]:
        query = db.query(Event)
        if lab_id:
            query = query.filter(Event.lab_id == lab_id)
        if severity:
            query = query.filter(Event.severity == severity)
        return query.order_by(Event.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Event:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise NotFoundError("Event", event_id)
        return event


event_service = EventService()

