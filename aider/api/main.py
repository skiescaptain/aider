from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import psutil

from .routes import repomap
from .models import ErrorResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track start time for uptime calculation
START_TIME = time.time()

app = FastAPI(
    title="Aider Repository Map Service",
    description="API service for generating repository maps using Aider technology",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(repomap.router, prefix="/api/v1/repomap", tags=["repomap"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            details={"type": str(type(exc)), "message": str(exc)}
        ).dict(),
    )

@app.get("/health")
async def health_check():
    """Health check endpoint that returns service status and basic metrics."""
    try:
        # Calculate uptime
        uptime = int(time.time() - START_TIME)
        
        # Get basic system metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": int(time.time()),
            "uptime_seconds": uptime,
            "system": {
                "memory_used_percent": memory.percent,
                "disk_used_percent": disk.percent
            },
            "version": app.version
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )