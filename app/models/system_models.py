"""
🌟 Polaris System Detection API - Pydantic Models
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class GPUInfo(BaseModel):
    """GPU information model"""
    name: str
    total_memory: Union[int, str]
    free_memory: Union[int, str]
    used_memory: Union[int, str]
    utilization: Union[int, str]


class GPUSummary(BaseModel):
    """GPU summary for realtime monitoring"""
    name: str
    utilization: Union[int, str]
    memory_used_percent: Union[float, str]


class MemoryInfo(BaseModel):
    """Memory information model"""
    total: int
    available: int
    percent: float
    used: int
    free: int


class DiskInfo(BaseModel):
    """Disk information model"""
    total: int
    used: int
    free: int
    percent: float


class CPUInfo(BaseModel):
    """CPU information model"""
    architecture: str
    cpu_percent: float
    cpu_count: int
    cpu_freq: Optional[Dict[str, Any]] = None
    load_avg: Optional[List[float]] = None


class NetworkInterface(BaseModel):
    """Network interface model"""
    family: int
    address: str
    netmask: Optional[str] = None
    broadcast: Optional[str] = None
    ptp: Optional[str] = None


class NetworkStats(BaseModel):
    """Network stats model"""
    isup: bool
    duplex: int
    speed: int
    mtu: int


class SystemDetectionResponse(BaseModel):
    """Complete system detection response"""
    api_name: str = Field(default="Polaris System Detection API")
    version: str = Field(default="1.0.0")
    
    # Platform info
    cpu: str
    name: str
    platform: str
    python_version: str
    os: str
    os_alias: List[str]
    
    # Device info
    device: str
    device_type: str
    cuda_version: str
    pytorch_version: str
    
    # Environment
    conda_environment: Optional[str] = None
    conda_prefix: Optional[str] = None
    
    # Real-time metrics
    cpu_percent: float
    cpu_count: int
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    gpu: List[GPUInfo]
    gpu_memory: str = ""
    
    # Optional Mac metrics
    mac_metrics: Optional[Dict[str, Any]] = None
    
    # Timestamp
    detection_timestamp: float


class GPUDetectionResponse(BaseModel):
    """GPU detection response"""
    polaris_gpu_detection: List[GPUInfo]
    device: str
    device_type: str
    cuda_version: str
    detection_timestamp: float


class CPUDetectionResponse(BaseModel):
    """CPU detection response"""
    polaris_cpu_detection: CPUInfo
    detection_timestamp: float


class MemoryDetectionResponse(BaseModel):
    """Memory detection response"""
    polaris_memory_detection: Dict[str, Any]
    detection_timestamp: float


class DiskDetectionResponse(BaseModel):
    """Disk detection response"""
    polaris_disk_detection: Dict[str, Any]
    detection_timestamp: float


class NetworkDetectionResponse(BaseModel):
    """Network detection response"""
    polaris_network_detection: Dict[str, Any]
    detection_timestamp: float


class EnvironmentDetectionResponse(BaseModel):
    """Environment detection response"""
    polaris_environment_detection: Dict[str, Any]
    detection_timestamp: float


class RealtimeMonitoringResponse(BaseModel):
    """Realtime monitoring response"""
    polaris_realtime_monitoring: Dict[str, Any]
    detection_timestamp: float


class PolarisRootResponse(BaseModel):
    """Root endpoint response"""
    api_name: str = "🌟 Polaris System Detection API"
    version: str = "1.0.0"
    description: str = "Advanced real-time system monitoring and hardware detection"
    endpoints: Dict[str, str]
    system_summary: Dict[str, str]
    polaris_status: str = "🌟 Active and detecting"


class HealthResponse(BaseModel):
    """Health check response"""
    polaris_status: str = "healthy"
    timestamp: float
    version: str = "1.0.0"


class TransformerLabCompatibleResponse(BaseModel):
    """Legacy compatible response format"""
    cpu: str
    name: str
    platform: str
    python_version: str
    os: str
    os_alias: List[str]
    gpu: List[GPUInfo]
    gpu_memory: str
    device: str
    device_type: str
    cuda_version: str
    conda_environment: Optional[str]
    conda_prefix: Optional[str]
    pytorch_version: str
    cpu_percent: float
    cpu_count: int
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    mac_metrics: Optional[Dict[str, Any]] = None 