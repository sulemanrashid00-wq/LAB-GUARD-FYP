from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate
from app.core.errors import NotFoundError


class AlertService:
    @staticmethod
    def create_alert(db: Session, data: AlertCreate) -> Alert:
        alert = Alert(
            lab_id=data.lab_id,
            event_id=data.event_id,
            title=data.title,
            description=data.description,
            severity=data.severity,
            status="active",
            created_at=datetime.now(timezone.utc)
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def get_alerts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
        lab_id: Optional[int] = None
    ) -> List[Alert]:
        query = db.query(Alert)
        if status_filter:
            query = query.filter(Alert.status == status_filter)
        if lab_id:
            query = query.filter(Alert.lab_id == lab_id)
        return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Alert:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise NotFoundError("Alert", alert_id)
        return alert

    @staticmethod
    def update_alert(db: Session, alert_id: int, data: AlertUpdate, current_user_id: int) -> Alert:
        alert = AlertService.get_alert_by_id(db, alert_id)
        if data.status == "acknowledged":
            alert.status = "acknowledged"
            alert.acknowledged_by_id = current_user_id
            alert.acknowledged_at = datetime.now(timezone.utc)
        elif data.status == "resolved":
            alert.status = "resolved"
            alert.resolved_by_id = current_user_id
            alert.resolved_at = datetime.now(timezone.utc)
        elif data.status:
            alert.status = data.status

        db.commit()
        db.refresh(alert)
        return alert


alert_service = AlertService()

