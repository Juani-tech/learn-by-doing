"""API main router."""
from fastapi import APIRouter
from app.api.v1.paths import router as paths_router

api_router = APIRouter()

# Include path routes
api_router.include_router(
    paths_router,
    prefix="/paths",
    tags=["paths"]
)
