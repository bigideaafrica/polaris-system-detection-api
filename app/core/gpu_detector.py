"""
🌟 Polaris System Detection API - GPU Detection Module
"""

from typing import Any, Dict, List, Optional

import torch

from app.utils.system_utils import bytes_to_string, is_wsl

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


class GPUDetector:
    """GPU detection and monitoring class"""
    
    def __init__(self):
        self.is_wsl = is_wsl()
        self.device_info = self._initialize_gpu()
    
    def _initialize_gpu(self) -> Dict[str, Any]:
        """Initialize GPU detection and get device information"""
        device_info = {
            "device": "cpu",
            "device_type": "cpu",
            "cuda_version": "n/a",
            "has_nvidia": HAS_NVIDIA,
            "has_amd": HAS_AMD,
            "pytorch_version": torch.__version__
        }
        
        print(f"🔥 PyTorch version: {torch.__version__}")
        
        # Determine which device to use (cuda/mps/cpu)
        if torch.cuda.is_available():
            device_info["device"] = "cuda"
            
            if HAS_NVIDIA:
                try:
                    nvmlInit()
                    device_info["cuda_version"] = torch.version.cuda
                    device_info["device_type"] = "nvidia"
                    pytorch_device = "CUDA"
                    print(f"🌟 PyTorch using {pytorch_device}, version {device_info['cuda_version']}")
                except Exception as e:
                    print(f"⚠️ Error initializing NVIDIA GPU: {e}")
                    
            elif HAS_AMD:
                try:
                    if not self.is_wsl:
                        rocml.smi_initialize()
                    device_info["device_type"] = "amd"
                    device_info["cuda_version"] = torch.version.hip
                    pytorch_device = "ROCm"
                    print(f"🌟 PyTorch using {pytorch_device}, version {device_info['cuda_version']}")
                except Exception as e:
                    print(f"⚠️ Error initializing AMD GPU: {e}")
                    
        elif torch.backends.mps.is_available():
            device_info["device"] = "mps"
            device_info["device_type"] = "apple_silicon"
            print("🌟 PyTorch using MPS for Apple Metal acceleration")
        
        return device_info
    
    def get_gpu_info(self) -> List[Dict[str, Any]]:
        """Get detailed GPU information for all detected GPUs"""
        gpu_list = []
        
        try:
            # Determine device count
            if HAS_AMD and not self.is_wsl:
                device_count = rocml.smi_get_device_count()
            elif HAS_NVIDIA:
                device_count = nvmlDeviceGetCount()
            else:
                return []

            for i in range(device_count):
                info = {}
                
                # Get device handle
                if HAS_AMD and not self.is_wsl:
                    handle = rocml.smi_get_device_id(i)
                elif HAS_NVIDIA:
                    handle = nvmlDeviceGetHandleByIndex(i)
                else:
                    continue

                # Get device name
                if HAS_NVIDIA:
                    device_name = nvmlDeviceGetName(handle)
                elif HAS_AMD and not self.is_wsl:
                    device_name = rocml.smi_get_device_name(i)
                else:
                    continue

                # Handle byte string conversion
                device_name = bytes_to_string(device_name)
                info["name"] = device_name

                # Get memory and utilization info
                if HAS_NVIDIA:
                    memory = nvmlDeviceGetMemoryInfo(handle)
                    info["total_memory"] = memory.total
                    info["free_memory"] = memory.free
                    info["used_memory"] = memory.used

                    utilization = nvmlDeviceGetUtilizationRates(handle)
                    info["utilization"] = utilization.gpu
                    
                elif HAS_AMD and not self.is_wsl:
                    info["total_memory"] = rocml.smi_get_device_memory_total(i)
                    info["used_memory"] = rocml.smi_get_device_memory_used(i)
                    info["free_memory"] = info["total_memory"] - info["used_memory"]
                    info["utilization"] = rocml.smi_get_device_utilization(i)

                gpu_list.append(info)
                
        except Exception as e:
            print(f"⚠️ Error getting GPU info: {e}")
            # Return CPU fallback
            gpu_list.append({
                "name": "cpu",
                "total_memory": "n/a",
                "free_memory": "n/a",
                "used_memory": "n/a",
                "utilization": "n/a",
            })

        return gpu_list
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get current device information"""
        return self.device_info.copy()
    
    def get_gpu_summary(self) -> List[Dict[str, Any]]:
        """Get summarized GPU information for realtime monitoring"""
        gpu_info = self.get_gpu_info()
        summary = []
        
        for gpu in gpu_info:
            gpu_summary = {
                "name": gpu["name"],
                "utilization": gpu["utilization"],
            }
            
            # Calculate memory usage percentage
            if (gpu["total_memory"] != "n/a" and 
                gpu["used_memory"] != "n/a" and 
                gpu["total_memory"] > 0):
                gpu_summary["memory_used_percent"] = round(
                    (gpu["used_memory"] / gpu["total_memory"]) * 100, 2
                )
            else:
                gpu_summary["memory_used_percent"] = "n/a"
                
            summary.append(gpu_summary)
        
        return summary 