"""
🌟 Polaris System Detection API - LEGACY VERSION
Real-time system information and hardware detection server
Note: This is the legacy single-file version. Use 'python main.py' for the new modular version.
"""

import asyncio
import json
import os
import platform
import subprocess
import sys
from typing import AsyncGenerator

# System monitoring
import psutil
import torch
import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

# GPU Detection Libraries
try:
    from pynvml import (nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex,
                        nvmlDeviceGetMemoryInfo, nvmlDeviceGetName,
                        nvmlDeviceGetUtilizationRates, nvmlInit)
    HAS_NVIDIA = True
except Exception:
    HAS_NVIDIA = False

try:
    from pyrsmi import rocml
    HAS_AMD = True
except Exception:
    HAS_AMD = False

# Create Polaris API app
app = FastAPI(
    title="🌟 Polaris System Detection API",
    description="Advanced real-time system monitoring and hardware detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create router
router = APIRouter(prefix="/polaris", tags=["polaris-detection"])

def is_wsl():
    """Detect if running on Windows Subsystem for Linux"""
    try:
        kernel_output = subprocess.check_output(["uname", "-r"], text=True).lower()
        return "microsoft" in kernel_output or "wsl2" in kernel_output
    except subprocess.CalledProcessError:
        return False

# Initialize system detection
IS_WSL_SYSTEM = is_wsl()
if IS_WSL_SYSTEM:
    print("🏄 Polaris detected WSL environment")

# Initialize static system information
polaris_system_info = {
    "api_name": "Polaris System Detection API",
    "cpu": platform.machine(),
    "name": platform.node(),
    "platform": platform.platform(),
    "python_version": platform.python_version(),
    "os": platform.system(),
    "os_alias": platform.system_alias(platform.system(), platform.release(), platform.version()),
    "gpu": [],
    "gpu_memory": "",
    "device": "cpu",
    "device_type": "cpu",
    "cuda_version": "n/a",
    "conda_environment": os.environ.get("CONDA_DEFAULT_ENV", "n/a"),
    "conda_prefix": os.environ.get("CONDA_PREFIX", "n/a"),
    "pytorch_version": torch.__version__,
    "polaris_version": "1.0.0"
}

# GPU Detection and Initialization
print(f"🔥 Polaris detected PyTorch version: {torch.__version__}")

# Determine which device to use (cuda/mps/cpu)
if torch.cuda.is_available():
    polaris_system_info["device"] = "cuda"
    if HAS_NVIDIA:
        try:
            nvmlInit()
            polaris_system_info["cuda_version"] = torch.version.cuda
            polaris_system_info["device_type"] = "nvidia"
            pytorch_device = "CUDA"
            print(f"🌟 Polaris: PyTorch using {pytorch_device}, version {polaris_system_info['cuda_version']}")
        except Exception as e:
            print(f"⚠️ Polaris: Error initializing NVIDIA GPU: {e}")
    elif HAS_AMD:
        try:
            if not IS_WSL_SYSTEM:
                rocml.smi_initialize()
            polaris_system_info["device_type"] = "amd"
            polaris_system_info["cuda_version"] = torch.version.hip
            pytorch_device = "ROCm"
            print(f"🌟 Polaris: PyTorch using {pytorch_device}, version {polaris_system_info['cuda_version']}")
        except Exception as e:
            print(f"⚠️ Polaris: Error initializing AMD GPU: {e}")

elif torch.backends.mps.is_available():
    polaris_system_info["device"] = "mps"
    polaris_system_info["device_type"] = "apple_silicon"
    print("🌟 Polaris: PyTorch using MPS for Apple Metal acceleration")

async def get_mac_disk_usage():
    """Get macOS-specific disk usage via diskutil"""
    if sys.platform != "darwin":
        return None

    try:
        process = await asyncio.create_subprocess_shell(
            "diskutil apfs list | awk '/Capacity In Use By Volumes/'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if stderr:
            print(f"⚠️ Polaris: Error retrieving disk usage: {stderr.decode().strip()}")
            return None

        mac_disk_usage = stdout.decode("utf-8").strip()

        if "Capacity In Use By Volumes:" in mac_disk_usage:
            mac_disk_usage_cleaned = int(
                mac_disk_usage.split("Capacity In Use By Volumes:")[1].strip().split("B")[0].strip()
            )
            return mac_disk_usage_cleaned

    except Exception as e:
        print(f"⚠️ Polaris: Error retrieving disk usage: {e}")

    return None

async def get_macmon_data():
    """Get detailed Mac system metrics via macmon library"""
    if sys.platform != "darwin":
        return None

    try:
        from macmon import MacMon
        macmon = MacMon()
        data = await macmon.get_metrics_async()
        json_data = json.loads(data)
        return json_data
    except Exception as e:
        print(f"⚠️ Polaris: Error retrieving macmon data: {e}")
        return None

def get_gpu_info():
    """Get detailed GPU information for all detected GPUs"""
    gpu_list = []
    
    try:
        # Determine device count
        if HAS_AMD and not IS_WSL_SYSTEM:
            device_count = rocml.smi_get_device_count()
        elif HAS_NVIDIA:
            device_count = nvmlDeviceGetCount()
        else:
            return []

        for i in range(device_count):
            info = {}
            
            # Get device handle
            if HAS_AMD and not IS_WSL_SYSTEM:
                handle = rocml.smi_get_device_id(i)
            elif HAS_NVIDIA:
                handle = nvmlDeviceGetHandleByIndex(i)
            else:
                continue

            # Get device name
            if HAS_NVIDIA:
                device_name = nvmlDeviceGetName(handle)
            elif HAS_AMD and not IS_WSL_SYSTEM:
                device_name = rocml.smi_get_device_name(i)
            else:
                continue

            # Handle byte string conversion
            if isinstance(device_name, bytes):
                device_name = device_name.decode(errors="ignore")

            info["name"] = device_name

            # Get memory and utilization info
            if HAS_NVIDIA:
                memory = nvmlDeviceGetMemoryInfo(handle)
                info["total_memory"] = memory.total
                info["free_memory"] = memory.free
                info["used_memory"] = memory.used

                utilization = nvmlDeviceGetUtilizationRates(handle)
                info["utilization"] = utilization.gpu
                
            elif HAS_AMD and not IS_WSL_SYSTEM:
                info["total_memory"] = rocml.smi_get_device_memory_total(i)
                info["used_memory"] = rocml.smi_get_device_memory_used(i)
                info["free_memory"] = info["total_memory"] - info["used_memory"]
                info["utilization"] = rocml.smi_get_device_utilization(i)

            gpu_list.append(info)
            
    except Exception as e:
        print(f"⚠️ Polaris: Error getting GPU info: {e}")
        # Return CPU fallback
        gpu_list.append({
            "name": "cpu",
            "total_memory": "n/a",
            "free_memory": "n/a",
            "used_memory": "n/a",
            "utilization": "n/a",
        })

    return gpu_list

@router.get("/detect")
async def polaris_system_detection():
    """🌟 Polaris primary detection endpoint - Complete system information"""
    # Start with static system information
    result = polaris_system_info.copy()

    # Get Mac-specific disk usage
    mac_disk_usage = await get_mac_disk_usage()

    # Get Mac monitoring data
    macmon_data = await get_macmon_data()

    # Get disk usage
    disk_usage = psutil.disk_usage("/")._asdict()
    if mac_disk_usage:
        disk_usage["used"] = mac_disk_usage
        disk_usage["free"] = disk_usage["total"] - mac_disk_usage
        disk_usage["percent"] = round((mac_disk_usage / disk_usage["total"]) * 100, 2)

    # Update with real-time performance metrics
    result.update({
        "cpu_percent": psutil.cpu_percent(),
        "cpu_count": psutil.cpu_count(),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": disk_usage,
        "gpu_memory": "",
        "detection_timestamp": asyncio.get_event_loop().time()
    })

    # Add Mac metrics if available
    if macmon_data:
        result["mac_metrics"] = macmon_data

    # Add GPU information
    result["gpu"] = get_gpu_info()

    return result

@router.get("/gpu")
async def polaris_gpu_detection():
    """🎮 Polaris GPU detection - Detailed GPU information only"""
    return {
        "polaris_gpu_detection": get_gpu_info(),
        "device": polaris_system_info["device"],
        "device_type": polaris_system_info["device_type"],
        "cuda_version": polaris_system_info["cuda_version"],
        "detection_timestamp": asyncio.get_event_loop().time()
    }

@router.get("/cpu")
async def polaris_cpu_detection():
    """🖥️ Polaris CPU detection - Detailed CPU information"""
    return {
        "polaris_cpu_detection": {
            "architecture": platform.machine(),
            "cpu_percent": psutil.cpu_percent(),
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else None,
        },
        "detection_timestamp": asyncio.get_event_loop().time()
    }

@router.get("/memory")
async def polaris_memory_detection():
    """💾 Polaris Memory detection - Detailed memory information"""
    return {
        "polaris_memory_detection": {
            "virtual_memory": psutil.virtual_memory()._asdict(),
            "swap_memory": psutil.swap_memory()._asdict(),
        },
        "detection_timestamp": asyncio.get_event_loop().time()
    }

@router.get("/disk")
async def polaris_disk_detection():
    """💿 Polaris Disk detection - Detailed disk information"""
    mac_disk_usage = await get_mac_disk_usage()
    disk_usage = psutil.disk_usage("/")._asdict()
    
    if mac_disk_usage:
        disk_usage["used"] = mac_disk_usage
        disk_usage["free"] = disk_usage["total"] - mac_disk_usage
        disk_usage["percent"] = round((mac_disk_usage / disk_usage["total"]) * 100, 2)
    
    return {
        "polaris_disk_detection": {
            "disk_usage": disk_usage,
            "disk_partitions": [p._asdict() for p in psutil.disk_partitions()],
        },
        "detection_timestamp": asyncio.get_event_loop().time()
    }

@router.get("/network")
async def polaris_network_detection():
    """🌐 Polaris Network detection - Network interface information"""
    return {
        "polaris_network_detection": {
            "network_io": psutil.net_io_counters()._asdict(),
            "network_interfaces": {
                name: [addr._asdict() for addr in addrs] 
                for name, addrs in psutil.net_if_addrs().items()
            },
            "network_stats": {
                name: stats._asdict() 
                for name, stats in psutil.net_if_stats().items()
            },
        },
        "detection_timestamp": asyncio.get_event_loop().time()
    }

@router.get("/environment")
async def polaris_environment_detection():
    """🐍 Polaris Environment detection - Python and PyTorch environment"""
    packages_info = {}
    pytorch_env = {}
    
    try:
        packages = subprocess.check_output(
            sys.executable + " -m pip list --format=json", 
            shell=True
        )
        packages = packages.decode("utf-8")
        packages_info = {"packages": json.loads(packages)}
    except Exception as e:
        packages_info = {"error": f"Failed to get Python packages: {e}"}

    try:
        output = subprocess.check_output(
            sys.executable + " -m torch.utils.collect_env", 
            shell=True
        )
        pytorch_env = {"pytorch_env": output.decode("utf-8")}
    except Exception as e:
        pytorch_env = {"error": f"Failed to get PyTorch environment: {e}"}

    return {
        "polaris_environment_detection": {
            **packages_info,
            **pytorch_env
        },
        "detection_timestamp": asyncio.get_event_loop().time()
    }

@router.get("/realtime")
async def polaris_realtime_monitoring():
    """⚡ Polaris Real-time monitoring - Lightweight performance metrics"""
    return {
        "polaris_realtime_monitoring": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "gpu_status": [
                {
                    "name": gpu["name"],
                    "utilization": gpu["utilization"],
                    "memory_used_percent": (
                        round((gpu["used_memory"] / gpu["total_memory"]) * 100, 2)
                        if gpu["total_memory"] != "n/a" and gpu["used_memory"] != "n/a"
                        else "n/a"
                    )
                }
                for gpu in get_gpu_info()
            ]
        },
        "detection_timestamp": asyncio.get_event_loop().time()
    }

# Add router to app
app.include_router(router)

@app.get("/")
async def polaris_root():
    """🌟 Polaris System Detection API - Root endpoint"""
    return {
        "api_name": "🌟 Polaris System Detection API",
        "version": "1.0.0",
        "description": "Advanced real-time system monitoring and hardware detection",
        "endpoints": {
            "/polaris/detect": "🌟 Complete system detection",
            "/polaris/gpu": "🎮 GPU detection only",
            "/polaris/cpu": "🖥️ CPU detection only", 
            "/polaris/memory": "💾 Memory detection only",
            "/polaris/disk": "💿 Disk detection only",
            "/polaris/network": "🌐 Network detection only",
            "/polaris/environment": "🐍 Python/PyTorch environment",
            "/polaris/realtime": "⚡ Real-time monitoring"
        },
        "system_summary": {
            "os": polaris_system_info["os"],
            "device_type": polaris_system_info["device_type"],
            "pytorch_device": polaris_system_info["device"]
        },
        "polaris_status": "🌟 Active and detecting"
    }

@app.get("/health")
async def polaris_health():
    """💚 Polaris health check"""
    return {
        "polaris_status": "healthy", 
        "timestamp": asyncio.get_event_loop().time(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print("🌟 ================================")
    print("🌟  POLARIS SYSTEM DETECTION API")
    print("🌟 ================================")
    print(f"📊 System Detected: {polaris_system_info['os']} with {polaris_system_info['device_type']} support")
    print(f"🚀 Starting Polaris on http://localhost:8339")
    print("🌟 ================================")
    
    uvicorn.run(
        "polaris_api:app",
        host="0.0.0.0", 
        port=8339,
        reload=True,
        log_level="info"
    )