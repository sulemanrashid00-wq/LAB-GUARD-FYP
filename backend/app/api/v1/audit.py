from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_admin
from app.models.user import User
from app.schemas.audit import AuditLogResponse
from app.schemas.common import APIResponse
from app.services.audit_service import audit_service

router = APIRouter(prefix="/audit", tags=["Security Audit Trail"])


@router.get("", response_model=APIResponse[List[AuditLogResponse]])
def get_audit_trail(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Retrieve audit trail of all security-sensitive actions (Admin only).
    """
    logs = audit_service.get_audit_logs(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        resource_type=resource_type,
        action=action
    )
    return APIResponse(data=logs)

