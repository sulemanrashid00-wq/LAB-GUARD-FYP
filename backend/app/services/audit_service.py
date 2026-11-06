from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogCreate


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details_json=details or {},
            created_at=datetime.now(timezone.utc)
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    @staticmethod
    def get_audit_logs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None
    ) -> List[AuditLog]:
        query = db.query(AuditLog)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if action:
            query = query.filter(AuditLog.action.ilike(f"%{action}%"))
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


audit_service = AuditService()

