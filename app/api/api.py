from fastapi import APIRouter
from app.api.endpoints import auth, doctors, patients, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
