from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    details_json: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    user_id: Optional[Any] = None


class AuditLogResponse(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: Any
    user_id: Optional[Any] = None
    created_at: datetime


