"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.session import init_db
from app.api.routes import health, analyze, modes, workspace, live_meeting


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("[DevPilot] Starting DevPilot AI Backend...")
    init_db()
    print("[DevPilot] Database initialized")
    yield
    # Shutdown
    print("[DevPilot] Shutting down DevPilot AI Backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered developer workspace for code analysis and generation",
    lifespan=lifespan,
)

# Configure CORS — allow all origins for hackathon dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(modes.router, prefix="/api/modes", tags=["AI Modes"])
app.include_router(workspace.router, prefix="/api/workspace", tags=["Workspace"])
app.include_router(live_meeting.router, prefix="/api/live-meeting", tags=["Live Meeting"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )

# Made with Bob
