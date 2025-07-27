"""
🌟 Polaris System Detection API - Main Application Routes
"""

import asyncio

from fastapi import APIRouter

from app.config.settings import settings
from app.core.polaris_manager import PolarisManager
from app.models.system_models import HealthResponse, PolarisRootResponse

# Create router for main application routes
router = APIRouter(tags=["main"])

# Initialize Polaris manager
polaris_manager = PolarisManager()


@router.get("/", response_model=PolarisRootResponse)
async def polaris_root():
    """🌟 Polaris System Detection API - Root endpoint"""
    system_summary = polaris_manager.get_system_summary()
    
    endpoints = {
        "/polaris/detect": "🌟 Complete system detection",
        "/polaris/gpu": "🎮 GPU detection only",
        "/polaris/cpu": "🖥️ CPU detection only", 
        "/polaris/memory": "💾 Memory detection only",
        "/polaris/disk": "💿 Disk detection only",
        "/polaris/network": "🌐 Network detection only",
        "/polaris/environment": "🐍 Python/PyTorch environment",
        "/polaris/realtime": "⚡ Real-time monitoring"
    }
    
    # Add legacy compatibility endpoints if enabled
    if settings.legacy_compatible:
        endpoints.update({
            "/server/info": "🔄 Legacy compatible system info",
            "/server/python_libraries": "🔄 Legacy compatible Python packages",
            "/server/pytorch_collect_env": "🔄 Legacy compatible PyTorch env"
        })
    
    return {
        "api_name": settings.title,
        "version": settings.version,
        "description": settings.description,
        "endpoints": endpoints,
        "system_summary": system_summary,
        "polaris_status": "🌟 Active and detecting"
    }


@router.get("/health", response_model=HealthResponse)
async def polaris_health():
    """💚 Polaris health check"""
    return {
        "polaris_status": "healthy", 
        "timestamp": asyncio.get_event_loop().time(),
        "version": settings.version
    } 