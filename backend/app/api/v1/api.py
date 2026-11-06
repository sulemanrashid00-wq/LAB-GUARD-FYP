from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.devices import router as devices_router
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.events import router as events_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.policies import router as policies_router
from app.api.v1.commands import router as commands_router
from app.api.v1.audit import router as audit_router
from app.api.v1.iot import router as iot_router
from app.api.v1.ai import router as ai_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(devices_router)
api_router.include_router(telemetry_router)
api_router.include_router(events_router)
api_router.include_router(alerts_router)
api_router.include_router(policies_router)
api_router.include_router(commands_router)
api_router.include_router(audit_router)
api_router.include_router(iot_router)
api_router.include_router(ai_router)

