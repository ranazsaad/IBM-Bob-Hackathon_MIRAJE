"""Health check endpoints"""

from fastapi import APIRouter
from datetime import datetime

from app.config import settings
from app.api.schemas.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
    )

# Made with Bob
