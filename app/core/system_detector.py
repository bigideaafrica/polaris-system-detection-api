"""
🌟 Polaris System Detection API - System Detection Module
"""

import asyncio
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

import psutil

from app.utils.system_utils import get_platform_info, safe_subprocess_run


class SystemDetector:
    """System detection and monitoring class"""
    
    def __init__(self):
        self.platform_info = get_platform_info()
    
    async def get_mac_disk_usage(self) -> Optional[int]:
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
                print(f"⚠️ Error retrieving disk usage: {stderr.decode().strip()}")
                return None

            mac_disk_usage = stdout.decode("utf-8").strip()

            if "Capacity In Use By Volumes:" in mac_disk_usage:
                mac_disk_usage_cleaned = int(
                    mac_disk_usage.split("Capacity In Use By Volumes:")[1].strip().split("B")[0].strip()
                )
                return mac_disk_usage_cleaned

        except Exception as e:
            print(f"⚠️ Error retrieving disk usage: {e}")

        return None

    async def get_macmon_data(self) -> Optional[Dict[str, Any]]:
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
            print(f"⚠️ Error retrieving macmon data: {e}")
            return None
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information"""
        cpu_info = {
            "architecture": self.platform_info["cpu"],
            "cpu_percent": psutil.cpu_percent(),
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        }
        
        # Add load average if available (Unix systems)
        if hasattr(os, 'getloadavg'):
            cpu_info["load_avg"] = os.getloadavg()
        
        return cpu_info
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information"""
        return {
            "virtual_memory": psutil.virtual_memory()._asdict(),
            "swap_memory": psutil.swap_memory()._asdict(),
        }
    
    async def get_disk_info(self) -> Dict[str, Any]:
        """Get detailed disk information"""
        # Get Mac-specific disk usage if available
        mac_disk_usage = await self.get_mac_disk_usage()
        disk_usage = psutil.disk_usage("/")._asdict()
        
        if mac_disk_usage:
            disk_usage["used"] = mac_disk_usage
            disk_usage["free"] = disk_usage["total"] - mac_disk_usage
            disk_usage["percent"] = round((mac_disk_usage / disk_usage["total"]) * 100, 2)
        
        return {
            "disk_usage": disk_usage,
            "disk_partitions": [p._asdict() for p in psutil.disk_partitions()],
        }
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface information"""
        return {
            "network_io": psutil.net_io_counters()._asdict(),
            "network_interfaces": {
                name: [addr._asdict() for addr in addrs] 
                for name, addrs in psutil.net_if_addrs().items()
            },
            "network_stats": {
                name: stats._asdict() 
                for name, stats in psutil.net_if_stats().items()
            },
        }
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get Python and PyTorch environment information"""
        env_info = {}
        
        # Get Python packages
        try:
            packages = subprocess.check_output(
                sys.executable + " -m pip list --format=json", 
                shell=True
            )
            packages = packages.decode("utf-8")
            env_info["packages"] = json.loads(packages)
        except Exception as e:
            env_info["packages_error"] = f"Failed to get Python packages: {e}"

        # Get PyTorch environment
        try:
            output = subprocess.check_output(
                sys.executable + " -m torch.utils.collect_env", 
                shell=True
            )
            env_info["pytorch_env"] = output.decode("utf-8")
        except Exception as e:
            env_info["pytorch_env_error"] = f"Failed to get PyTorch environment: {e}"

        return env_info
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get lightweight real-time performance metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        }
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform information"""
        return self.platform_info.copy() 