from fastapi import APIRouter
from app.api.v1 import devices, auth, telemetry

api_router = APIRouter()

# Routers ko API v1 mein mount kar dein
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(devices.router)
api_router.include_router(telemetry.router, prefix="/agent", tags=["Agent Telemetry"])
api_router.include_router(telemetry.telemetry_router, prefix="/telemetry", tags=["Telemetry"])

