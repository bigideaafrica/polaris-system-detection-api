#!/usr/bin/env python3
"""
🌟 Polaris System Detection API - System Check Tool
Quick diagnostic tool to check system capabilities
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.polaris_manager import PolarisManager
from app.utils.system_utils import get_platform_info


async def main():
    """Run system diagnostics"""
    print("🌟 ================================")
    print("🌟  POLARIS SYSTEM CHECK TOOL")
    print("🌟 ================================")
    
    # Initialize Polaris manager
    try:
        polaris = PolarisManager()
        print("✅ Polaris Manager initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Polaris Manager: {e}")
        return
    
    # Check platform info
    print("\n📊 Platform Information:")
    platform_info = get_platform_info()
    for key, value in platform_info.items():
        print(f"   {key}: {value}")
    
    # Check GPU detection
    print("\n🎮 GPU Detection:")
    try:
        gpu_info = polaris.gpu_detector.get_gpu_info()
        device_info = polaris.gpu_detector.get_device_info()
        
        print(f"   Device: {device_info['device']}")
        print(f"   Device Type: {device_info['device_type']}")
        print(f"   CUDA Version: {device_info['cuda_version']}")
        print(f"   PyTorch Version: {device_info['pytorch_version']}")
        
        if gpu_info:
            print(f"   Found {len(gpu_info)} GPU(s):")
            for i, gpu in enumerate(gpu_info):
                print(f"     GPU {i}: {gpu['name']}")
                if gpu['total_memory'] != 'n/a':
                    print(f"       Memory: {gpu['used_memory']}/{gpu['total_memory']} bytes")
                    print(f"       Utilization: {gpu['utilization']}%")
        else:
            print("   No GPUs detected")
    except Exception as e:
        print(f"   ❌ GPU detection error: {e}")
    
    # Check system metrics
    print("\n🖥️  System Metrics:")
    try:
        cpu_info = polaris.system_detector.get_cpu_info()
        memory_info = polaris.system_detector.get_memory_info()
        
        print(f"   CPU: {cpu_info['architecture']}")
        print(f"   CPU Usage: {cpu_info['cpu_percent']}%")
        print(f"   CPU Count: {cpu_info['cpu_count']}")
        print(f"   Memory Usage: {memory_info['virtual_memory']['percent']}%")
        print(f"   Memory Total: {memory_info['virtual_memory']['total']} bytes")
    except Exception as e:
        print(f"   ❌ System metrics error: {e}")
    
    # Check network
    print("\n🌐 Network:")
    try:
        network_info = polaris.system_detector.get_network_info()
        interfaces = network_info['network_interfaces']
        print(f"   Found {len(interfaces)} network interfaces:")
        for name, addrs in list(interfaces.items())[:3]:  # Show first 3
            print(f"     {name}: {len(addrs)} addresses")
    except Exception as e:
        print(f"   ❌ Network detection error: {e}")
    
    print("\n🌟 ================================")
    print("🌟  System check completed!")
    print("🌟 ================================")


if __name__ == "__main__":
    asyncio.run(main()) 