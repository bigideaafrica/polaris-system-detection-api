"""
🌟 Polaris System Detection API - Polaris Manager
"""

import asyncio
import os
from typing import Any, Dict

from app.config.settings import settings
from app.core.gpu_detector import GPUDetector
from app.core.system_detector import SystemDetector
from app.utils.system_utils import get_platform_info


class PolarisManager:
    """Main Polaris system detection manager"""
    
    def __init__(self):
        self.gpu_detector = GPUDetector()
        self.system_detector = SystemDetector()
        self.platform_info = get_platform_info()
        self._base_system_info = self._initialize_base_info()
    
    def _initialize_base_info(self) -> Dict[str, Any]:
        """Initialize base system information"""
        device_info = self.gpu_detector.get_device_info()
        
        return {
            "api_name": settings.title,
            "version": settings.version,
            **self.platform_info,
            **device_info,
            "conda_environment": settings.conda_environment or "n/a",
            "conda_prefix": settings.conda_prefix or "n/a",
            "gpu_memory": "",
        }
    
    async def get_complete_system_info(self) -> Dict[str, Any]:
        """Get complete system information (main detection endpoint)"""
        # Start with base system info
        result = self._base_system_info.copy()
        
        # Get real-time system metrics
        cpu_info = self.system_detector.get_cpu_info()
        memory_info = self.system_detector.get_memory_info()
        disk_info = await self.system_detector.get_disk_info()
        
        # Get Mac-specific data if available
        macmon_data = await self.system_detector.get_macmon_data()
        
        # Update with real-time metrics
        result.update({
            "cpu_percent": cpu_info["cpu_percent"],
            "cpu_count": cpu_info["cpu_count"],
            "memory": memory_info["virtual_memory"],
            "disk": disk_info["disk_usage"],
            "detection_timestamp": asyncio.get_event_loop().time()
        })
        
        # Add Mac metrics if available
        if macmon_data:
            result["mac_metrics"] = macmon_data
        
        # Add GPU information
        result["gpu"] = self.gpu_detector.get_gpu_info()
        
        return result
    
    async def get_gpu_detection(self) -> Dict[str, Any]:
        """Get GPU detection information"""
        device_info = self.gpu_detector.get_device_info()
        
        return {
            "polaris_gpu_detection": self.gpu_detector.get_gpu_info(),
            "device": device_info["device"],
            "device_type": device_info["device_type"],
            "cuda_version": device_info["cuda_version"],
            "detection_timestamp": asyncio.get_event_loop().time()
        }
    
    def get_cpu_detection(self) -> Dict[str, Any]:
        """Get CPU detection information"""
        return {
            "polaris_cpu_detection": self.system_detector.get_cpu_info(),
            "detection_timestamp": asyncio.get_event_loop().time()
        }
    
    def get_memory_detection(self) -> Dict[str, Any]:
        """Get memory detection information"""
        return {
            "polaris_memory_detection": self.system_detector.get_memory_info(),
            "detection_timestamp": asyncio.get_event_loop().time()
        }
    
    async def get_disk_detection(self) -> Dict[str, Any]:
        """Get disk detection information"""
        return {
            "polaris_disk_detection": await self.system_detector.get_disk_info(),
            "detection_timestamp": asyncio.get_event_loop().time()
        }
    
    def get_network_detection(self) -> Dict[str, Any]:
        """Get network detection information"""
        return {
            "polaris_network_detection": self.system_detector.get_network_info(),
            "detection_timestamp": asyncio.get_event_loop().time()
        }
    
    def get_environment_detection(self) -> Dict[str, Any]:
        """Get environment detection information"""
        return {
            "polaris_environment_detection": self.system_detector.get_environment_info(),
            "detection_timestamp": asyncio.get_event_loop().time()
        }
    
    def get_realtime_monitoring(self) -> Dict[str, Any]:
        """Get real-time monitoring information"""
        realtime_metrics = self.system_detector.get_realtime_metrics()
        gpu_summary = self.gpu_detector.get_gpu_summary()
        
        return {
            "polaris_realtime_monitoring": {
                **realtime_metrics,
                "gpu_status": gpu_summary
            },
            "detection_timestamp": asyncio.get_event_loop().time()
        }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system summary for root endpoint"""
        device_info = self.gpu_detector.get_device_info()
        
        return {
            "os": self.platform_info["os"],
            "device_type": device_info["device_type"],
            "pytorch_device": device_info["device"]
        }
    
    async def get_transformer_lab_compatible_info(self) -> Dict[str, Any]:
        """Get Transformer Lab compatible system information"""
        # This mirrors the original Transformer Lab serverinfo.py response format
        result = self._base_system_info.copy()
        
        # Remove Polaris-specific fields for compatibility
        result.pop("api_name", None)
        result.pop("version", None)
        
        # Get real-time system metrics
        cpu_info = self.system_detector.get_cpu_info()
        memory_info = self.system_detector.get_memory_info()
        disk_info = await self.system_detector.get_disk_info()
        
        # Get Mac-specific data if available
        macmon_data = await self.system_detector.get_macmon_data()
        
        # Update with real-time metrics (Transformer Lab format)
        result.update({
            "cpu_percent": cpu_info["cpu_percent"],
            "cpu_count": cpu_info["cpu_count"],
            "memory": memory_info["virtual_memory"],
            "disk": disk_info["disk_usage"],
        })
        
        # Add Mac metrics if available
        if macmon_data:
            result["mac_metrics"] = macmon_data
        
        # Add GPU information
        result["gpu"] = self.gpu_detector.get_gpu_info()
        
        return result 