from fastapi import APIRouter
from app.api.v1 import (
    auth,
    devices,
    telemetry,
    events,
    alerts,
    policies,
    commands,
    audit,
    iot,
    ai,
)

api_router = APIRouter()

# 1. Authentication & Users (S-03)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# 2. Devices & Hardware Registry (S-04)
api_router.include_router(devices.router)

# 3. Agent Heartbeat & Telemetry Ingestion (S-05)
api_router.include_router(telemetry.router, prefix="/agent", tags=["Agent Telemetry"])
api_router.include_router(telemetry.telemetry_router, prefix="/telemetry", tags=["Telemetry"])

# 4. Security Events & Incidents (S-06)
api_router.include_router(events.router)

# 5. Policies & Compliance (S-07)
api_router.include_router(policies.router)

# 6. Alerts & Notifications (S-08)
api_router.include_router(alerts.router)

# 7. Remote Commands (S-09)
api_router.include_router(commands.router)

# 8. Audit Logs (S-10)
api_router.include_router(audit.router)

# 9. IoT Protocol Gateway (S-12)
api_router.include_router(iot.router)

# 10. AI Inference & Anomaly (S-12)
api_router.include_router(ai.router)

__all__ = ["api_router"]
