"""
🌟 Polaris System Detection API - Main Routes
"""

import asyncio

from fastapi import APIRouter

from app.config.settings import settings
from app.core.polaris_manager import PolarisManager
from app.models.system_models import (CPUDetectionResponse,
                                      DiskDetectionResponse,
                                      EnvironmentDetectionResponse,
                                      GPUDetectionResponse, HealthResponse,
                                      MemoryDetectionResponse,
                                      NetworkDetectionResponse,
                                      PolarisRootResponse,
                                      RealtimeMonitoringResponse,
                                      SystemDetectionResponse)

# Create router
router = APIRouter(prefix=settings.api_prefix, tags=["polaris-detection"])

# Initialize Polaris manager
polaris_manager = PolarisManager()


@router.get("/detect", response_model=SystemDetectionResponse)
async def polaris_system_detection():
    """🌟 Polaris primary detection endpoint - Complete system information"""
    return await polaris_manager.get_complete_system_info()


@router.get("/gpu", response_model=GPUDetectionResponse)
async def polaris_gpu_detection():
    """🎮 Polaris GPU detection - Detailed GPU information only"""
    return await polaris_manager.get_gpu_detection()


@router.get("/cpu", response_model=CPUDetectionResponse)
async def polaris_cpu_detection():
    """🖥️ Polaris CPU detection - Detailed CPU information"""
    return polaris_manager.get_cpu_detection()


@router.get("/memory", response_model=MemoryDetectionResponse)
async def polaris_memory_detection():
    """💾 Polaris Memory detection - Detailed memory information"""
    return polaris_manager.get_memory_detection()


@router.get("/disk", response_model=DiskDetectionResponse)
async def polaris_disk_detection():
    """💿 Polaris Disk detection - Detailed disk information"""
    return await polaris_manager.get_disk_detection()


@router.get("/network", response_model=NetworkDetectionResponse)
async def polaris_network_detection():
    """🌐 Polaris Network detection - Network interface information"""
    return polaris_manager.get_network_detection()


@router.get("/environment", response_model=EnvironmentDetectionResponse)
async def polaris_environment_detection():
    """🐍 Polaris Environment detection - Python and PyTorch environment"""
    return polaris_manager.get_environment_detection()


@router.get("/realtime", response_model=RealtimeMonitoringResponse)
async def polaris_realtime_monitoring():
    """⚡ Polaris Real-time monitoring - Lightweight performance metrics"""
    return polaris_manager.get_realtime_monitoring() 