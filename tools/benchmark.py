#!/usr/bin/env python3
"""
🌟 Polaris System Detection API - Benchmark Tool
Simple performance benchmark for API endpoints
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.polaris_manager import PolarisManager


async def benchmark_endpoint(name: str, func, *args, **kwargs):
    """Benchmark a single endpoint function"""
    print(f"\n🚀 Benchmarking {name}...")
    
    # Warmup
    try:
        await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
    except Exception as e:
        print(f"   ❌ Warmup failed: {e}")
        return
    
    # Benchmark
    times = []
    iterations = 10
    
    for i in range(iterations):
        start_time = time.perf_counter()
        try:
            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        except Exception as e:
            print(f"   ❌ Iteration {i+1} failed: {e}")
            return
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"   ✅ Average: {avg_time*1000:.2f}ms")
    print(f"   ⚡ Fastest: {min_time*1000:.2f}ms")
    print(f"   🐌 Slowest: {max_time*1000:.2f}ms")
    print(f"   📊 {iterations} iterations")


async def main():
    """Run API benchmarks"""
    print("🌟 ================================")
    print("🌟  POLARIS API BENCHMARK TOOL")
    print("🌟 ================================")
    
    # Initialize Polaris manager
    try:
        polaris = PolarisManager()
        print("✅ Polaris Manager initialized")
    except Exception as e:
        print(f"❌ Error initializing Polaris Manager: {e}")
        return
    
    # Benchmark endpoints
    benchmarks = [
        ("GPU Detection", polaris.get_gpu_detection),
        ("CPU Detection", polaris.get_cpu_detection),
        ("Memory Detection", polaris.get_memory_detection),
        ("Disk Detection", polaris.get_disk_detection),
        ("Network Detection", polaris.get_network_detection),
        ("Realtime Monitoring", polaris.get_realtime_monitoring),
        ("Complete System Info", polaris.get_complete_system_info),
    ]
    
    print(f"\n🏁 Running benchmarks for {len(benchmarks)} endpoints...")
    
    total_start = time.perf_counter()
    
    for name, func in benchmarks:
        await benchmark_endpoint(name, func)
    
    total_end = time.perf_counter()
    
    print(f"\n🌟 ================================")
    print(f"🌟  Total benchmark time: {(total_end - total_start)*1000:.2f}ms")
    print("🌟  Benchmark completed!")
    print("🌟 ================================")


if __name__ == "__main__":
    asyncio.run(main()) 