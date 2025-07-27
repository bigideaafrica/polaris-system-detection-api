# 🌟 Polaris Migration Guide

This guide helps you migrate from the old single-file structure to the new organized project structure.

## What Changed

### Old Structure (v1.0)
```
polaris-system-detection-api/
├── polaris_api.py          # Single 462-line file
├── polaris_api_fixed.py    # Single 320-line file  
├── requirements.txt
├── README.md
├── start_polaris.bat
└── start_polaris.sh
```

### New Structure (v2.0)
```
polaris-system-detection-api/
├── app/
│   ├── api/
│   │   ├── main_routes.py           # Root and health endpoints
│   │   ├── polaris_routes.py        # Main Polaris API routes
│   │   └── transformer_lab_routes.py # Compatibility routes
│   ├── core/
│   │   ├── gpu_detector.py          # GPU detection logic
│   │   ├── system_detector.py       # System monitoring
│   │   └── polaris_manager.py       # Main coordinator
│   ├── models/
│   │   └── system_models.py         # Pydantic response models
│   ├── utils/
│   │   └── system_utils.py          # Utility functions
│   ├── config/
│   │   └── settings.py              # Configuration management
│   └── main.py                      # FastAPI app creation
├── tools/
│   ├── system_check.py              # Diagnostic tool
│   └── benchmark.py                 # Performance testing
├── scripts/
│   ├── setup.py                     # Project setup
│   └── clean.py                     # Cleanup utility
├── main.py                          # Application entry point
├── requirements.txt                 # Updated dependencies
└── README.md                        # Updated documentation
```

## API Compatibility

### ✅ 100% Backward Compatible

All existing API endpoints continue to work exactly as before:

- `GET /polaris/detect` - Complete system detection
- `GET /polaris/gpu` - GPU information  
- `GET /polaris/cpu` - CPU information
- `GET /polaris/memory` - Memory information
- `GET /polaris/disk` - Disk information
- `GET /polaris/network` - Network information
- `GET /polaris/environment` - Python environment
- `GET /polaris/realtime` - Real-time monitoring
- `GET /server/info` - Legacy compatibility (optional)
- `GET /server/python_libraries` - Legacy packages (optional)
- `GET /server/pytorch_collect_env` - Legacy PyTorch env (optional)

### New Features

1. **Configuration Management** - Environment-based settings via `.env`
2. **Better Error Handling** - Structured error responses
3. **Type Safety** - Pydantic models for all responses
4. **Development Tools** - System check and benchmarking utilities
5. **Modular Design** - Easy to extend and maintain

## Migration Steps

### 1. Update Your Installation

```bash
# Backup your current setup (optional)
cp -r polaris-system-detection-api polaris-backup

# Pull the new structure
git pull  # or download the new version

# Run the setup script
python scripts/setup.py
```

### 2. Update Start Commands

**Old way:**
```bash
python polaris_api.py
```

**New way:**
```bash
python main.py
```

The start scripts (`start_polaris.bat` and `start_polaris.sh`) are automatically updated.

### 3. Environment Configuration (Optional)

Create a `.env` file for custom configuration:

```bash
# Server settings
POLARIS_HOST=0.0.0.0
POLARIS_PORT=8339

# Features
POLARIS_ENABLE_GPU_DETECTION=true
POLARIS_LEGACY_COMPATIBLE=false
```

### 4. Update Import Statements (If Using Programmatically)

**Old imports:**
```python
from polaris_api import app
```

**New imports:**
```python
from app.main import app
from app.core.polaris_manager import PolarisManager
```

## Benefits of New Structure

### 🏗️ **Better Organization**
- Clear separation of concerns
- Easy to find and modify specific functionality
- Reduced file sizes (no more 400+ line files)

### 🔧 **Easier Maintenance**
- Modular components can be updated independently
- Better error isolation
- Simplified testing

### 📈 **Enhanced Features**
- Configuration management
- Development tools
- Better documentation
- Type safety with Pydantic

### 🚀 **Better Performance**
- Lazy loading of GPU libraries
- Optimized imports
- Better memory management

## Troubleshooting

### Import Errors
```bash
# Run the system check
python tools/system_check.py

# Reinstall dependencies
pip install -r requirements.txt
```

### GPU Detection Issues
```bash
# Check GPU detection specifically
python -c "from app.core.gpu_detector import GPUDetector; print(GPUDetector().get_device_info())"
```

### Port Conflicts
```bash
# Change port in .env file
echo "POLARIS_PORT=8340" >> .env
```

## Rollback Plan

If you need to rollback to the old version:

1. Keep a backup of your old files
2. The old `polaris_api.py` and `polaris_api_fixed.py` files are preserved
3. Simply run the old files directly if needed

## Support

If you encounter any issues during migration:

1. Run `python tools/system_check.py` for diagnostics
2. Check the logs for specific error messages
3. Ensure all dependencies are installed: `pip install -r requirements.txt`
4. Try the setup script: `python scripts/setup.py`

The new structure maintains 100% API compatibility while providing a much better development experience. 