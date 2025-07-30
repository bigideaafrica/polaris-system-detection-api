"""
🌟 Polaris System Detection API - Configuration Settings
"""

import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class PolarisSettings(BaseSettings):
    """Configuration settings for Polaris API"""
    
    # API Configuration
    title: str = "🌟 Polaris System Detection API"
    description: str = "Advanced real-time system monitoring and hardware detection"
    version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = int(os.environ.get("PORT", 8339))
    reload: bool = True
    log_level: str = "info"
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # API Paths
    api_prefix: str = "/polaris"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Legacy Compatibility (disabled by default)
    legacy_compatible: bool = False
    legacy_port: int = 8338
    legacy_prefix: str = "/server"
    
    # System Detection Configuration
    enable_gpu_detection: bool = True
    enable_mac_specific: bool = True
    enable_realtime_monitoring: bool = True
    
    # Monitoring Intervals (seconds)
    cpu_check_interval: float = 1.0
    memory_check_interval: float = 1.0
    disk_check_interval: float = 5.0
    gpu_check_interval: float = 2.0
    
    # Environment Detection
    conda_environment: Optional[str] = os.environ.get("CONDA_DEFAULT_ENV")
    conda_prefix: Optional[str] = os.environ.get("CONDA_PREFIX")
    
    class Config:
        env_file = ".env"
        env_prefix = "POLARIS_"


# Global settings instance
settings = PolarisSettings() 