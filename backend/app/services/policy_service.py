import operator
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.policy import Policy
from app.models.telemetry import Telemetry
from app.models.alert import Alert
from app.schemas.policy import PolicyCreate, PolicyUpdate
from app.core.errors import NotFoundError

OPERATORS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
}


class PolicyService:
    @staticmethod
    def create_policy(db: Session, data: PolicyCreate) -> Policy:
        policy = Policy(
            lab_id=data.lab_id,
            name=data.name,
            description=data.description,
            rule_type=data.rule_type,
            condition_operator=data.condition_operator,
            threshold_value=data.threshold_value,
            action_type=data.action_type,
            is_active=data.is_active,
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def get_policies(db: Session, lab_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[Policy]:
        query = db.query(Policy)
        if lab_id:
            query = query.filter(Policy.lab_id == lab_id)
        if is_active is not None:
            query = query.filter(Policy.is_active == is_active)
        return query.all()

    @staticmethod
    def get_policy_by_id(db: Session, policy_id: int) -> Policy:
        policy = db.query(Policy).filter(Policy.id == policy_id).first()
        if not policy:
            raise NotFoundError("Policy", policy_id)
        return policy

    @staticmethod
    def update_policy(db: Session, policy_id: int, data: PolicyUpdate) -> Policy:
        policy = PolicyService.get_policy_by_id(db, policy_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(policy, key, value)
        db.commit()
        db.refresh(policy)
        return policy

    @staticmethod
    def delete_policy(db: Session, policy_id: int) -> bool:
        policy = PolicyService.get_policy_by_id(db, policy_id)
        db.delete(policy)
        db.commit()
        return True

    @staticmethod
    def evaluate_telemetry(db: Session, telemetry: Telemetry, lab_id: int) -> List[str]:
        """
        Evaluates incoming telemetry data against active lab policies.
        Triggers alerts if policy thresholds are violated.
        """
        active_policies = db.query(Policy).filter(Policy.lab_id == lab_id, Policy.is_active == True).all()
        triggered_actions = []

        for pol in active_policies:
            val = None
            if pol.rule_type == "temperature_limit":
                val = telemetry.temperature
            elif pol.rule_type == "gas_limit":
                val = telemetry.gas_ppm
            elif pol.rule_type == "sound_limit":
                val = telemetry.sound_db

            if val is not None and pol.condition_operator in OPERATORS:
                comp_func = OPERATORS[pol.condition_operator]
                if comp_func(val, pol.threshold_value):
                    action_msg = f"Policy '{pol.name}' violated: {val} {pol.condition_operator} {pol.threshold_value}"
                    triggered_actions.append(action_msg)

                    # Automatically create an alert
                    alert = Alert(
                        lab_id=lab_id,
                        title=f"Policy Violation: {pol.name}",
                        description=f"Sensor reading {val} breached threshold {pol.threshold_value} ({pol.rule_type})",
                        severity="high" if "gas" in pol.rule_type or val > pol.threshold_value * 1.3 else "medium",
                        status="active"
                    )
                    db.add(alert)
                    db.commit()

        return triggered_actions


policy_service = PolicyService()

