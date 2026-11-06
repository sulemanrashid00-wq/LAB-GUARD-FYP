from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_current_active_admin
from app.models.user import User
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyResponse
from app.schemas.common import APIResponse
from app.services.policy_service import policy_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/policies", tags=["Policies & Automation Rules"])


@router.get("", response_model=APIResponse[List[PolicyResponse]])
def list_policies(
    lab_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List configured safety and security policies.
    """
    policies = policy_service.get_policies(db, lab_id=lab_id, is_active=is_active)
    return APIResponse(data=policies)


@router.get("/{policy_id}", response_model=APIResponse[PolicyResponse])
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve details of a specific policy rule.
    """
    policy = policy_service.get_policy_by_id(db, policy_id)
    return APIResponse(data=policy)


@router.post("", response_model=APIResponse[PolicyResponse], status_code=status.HTTP_201_CREATED)
def create_policy(
    policy_in: PolicyCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Create a new lab safety policy / threshold rule (Admin only).
    """
    policy = policy_service.create_policy(db, policy_in)
    audit_service.log_action(
        db,
        action="CREATE_POLICY",
        user_id=current_admin.id,
        resource_type="policy",
        resource_id=str(policy.id),
        details={"name": policy.name, "rule_type": policy.rule_type, "threshold": policy.threshold_value}
    )
    return APIResponse(message="Policy created", data=policy)


@router.patch("/{policy_id}", response_model=APIResponse[PolicyResponse])
def update_policy(
    policy_id: int,
    policy_in: PolicyUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Update policy rules or active status (Admin only).
    """
    policy = policy_service.update_policy(db, policy_id, policy_in)
    audit_service.log_action(
        db,
        action="UPDATE_POLICY",
        user_id=current_admin.id,
        resource_type="policy",
        resource_id=str(policy.id),
        details=policy_in.model_dump(exclude_unset=True)
    )
    return APIResponse(message="Policy updated", data=policy)


@router.delete("/{policy_id}", response_model=APIResponse[dict])
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Remove an operational policy rule (Admin only).
    """
    policy_service.delete_policy(db, policy_id)
    audit_service.log_action(
        db,
        action="DELETE_POLICY",
        user_id=current_admin.id,
        resource_type="policy",
        resource_id=str(policy_id)
    )
    return APIResponse(message="Policy deleted", data={"deleted_id": policy_id})

