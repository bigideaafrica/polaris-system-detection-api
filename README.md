# 🌟 Polaris System Detection API

A powerful standalone FastAPI server that provides comprehensive system information and hardware detection.

## Features

- **Multi-Platform Support**: Linux, macOS, Windows (via WSL)
- **GPU Detection**: NVIDIA (CUDA), AMD (ROCm), Apple Silicon (MPS)
- **Real-time Monitoring**: CPU, Memory, Disk, Network, GPU utilization
- **Hardware-Aware**: Automatically detects and optimizes for available hardware
- **RESTful API**: Clean JSON endpoints for all system information

## Quick Start

### Automated Setup

```bash
# Run the setup script (recommended)
python scripts/setup.py
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run Polaris
python main.py
```

### Using Start Scripts

**Windows:**
```cmd
start_polaris.bat
```

**Unix/macOS:**
```bash
./start_polaris.sh
```

The server will start on `http://localhost:8339`

## API Endpoints

### Core Endpoints

- `GET /` - 🌟 Polaris API information and system summary
- `GET /health` - 💚 Health check
- `GET /polaris/detect` - 🌟 Complete system detection

### Detailed Detection

- `GET /polaris/gpu` - 🎮 GPU detection only
- `GET /polaris/cpu` - 🖥️ CPU detection only  
- `GET /polaris/memory` - 💾 Memory detection only
- `GET /polaris/disk` - 💿 Disk detection only
- `GET /polaris/network` - 🌐 Network detection only

### Environment Detection

- `GET /polaris/environment` - 🐍 Python/PyTorch environment detection

### Real-time Monitoring

- `GET /polaris/realtime` - ⚡ Real-time performance monitoring

## Example Response

```json
{
  "api_name": "Polaris System Detection API",
  "cpu": "x86_64",
  "name": "MyComputer",
  "platform": "Linux-5.15.0-microsoft-standard-WSL2-x86_64",
  "python_version": "3.11.0",
  "os": "Linux",
  "device": "cuda",
  "device_type": "nvidia",
  "cuda_version": "12.1",
  "cpu_percent": 15.2,
  "cpu_count": 16,
  "memory": {
    "total": 34359738368,
    "available": 28991709184,
    "percent": 15.6
  },
  "gpu": [
    {
      "name": "NVIDIA GeForce RTX 4090",
      "total_memory": 25757220864,
      "free_memory": 23622190080,
      "used_memory": 2135030784,
      "utilization": 12
    }
  ],
  "detection_timestamp": 1643723400.123
}
```

## Hardware Detection

### GPU Support

**NVIDIA GPUs** (via pynvml):
- GPU count, names, memory usage
- Real-time utilization tracking
- CUDA version detection

**AMD GPUs** (via pyrsmi):
- ROCm support
- Memory and utilization tracking
- WSL compatibility

**Apple Silicon** (via PyTorch MPS):
- Metal Performance Shaders detection
- macOS-specific monitoring via macmon

### Platform-Specific Features

**Windows/WSL**:
- Automatic WSL detection
- Special handling for GPU libraries

**macOS**:
- Advanced disk usage via diskutil
- Detailed system metrics via macmon
- Apple Silicon SoC information

**Linux**:
- Full GPU support
- Standard psutil monitoring

## Dependencies

- **FastAPI**: Web framework
- **psutil**: Cross-platform system monitoring
- **torch**: Device detection (CUDA/MPS)
- **pynvml**: NVIDIA GPU monitoring
- **pyrsmi**: AMD GPU monitoring
- **macmon**: macOS system monitoring (optional)

## Usage Examples

### Check Polaris System Summary
```bash
curl http://localhost:8339/
```

### Get Real-time GPU Detection
```bash
curl http://localhost:8339/polaris/gpu
```

### Monitor System Performance
```bash
curl http://localhost:8339/polaris/realtime
```

### Complete System Detection
```bash
curl http://localhost:8339/polaris/detect
```

## Error Handling

The server gracefully handles:
- Missing GPU libraries
- Unsupported hardware
- Platform-specific failures
- Permission issues

Failed components return fallback values instead of crashing.

## Development

Run in development mode with auto-reload:

```bash
uvicorn polaris_api:app --reload --host 0.0.0.0 --port 8339
```

## API Documentation

- **Swagger UI**: http://localhost:8339/docs
- **ReDoc**: http://localhost:8339/redoc

## License

Based on Transformer Lab's implementation with similar functionality.

---

🌟 **Polaris System Detection API** - Advanced hardware detection made simple.