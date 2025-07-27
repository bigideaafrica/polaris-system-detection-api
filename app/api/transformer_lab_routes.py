"""
🌟 Polaris System Detection API - Legacy Compatibility Routes
"""

import json
import subprocess
import sys

from fastapi import APIRouter

from app.config.settings import settings
from app.core.polaris_manager import PolarisManager
from app.models.system_models import TransformerLabCompatibleResponse

# Create router for legacy compatibility
router = APIRouter(prefix=settings.legacy_prefix, tags=["legacy-compatible"])

# Initialize Polaris manager
polaris_manager = PolarisManager()


@router.get("/info", response_model=TransformerLabCompatibleResponse)
async def get_computer_information():
    """
    Legacy system information endpoint
    Provides system information in a standardized format
    """
    return await polaris_manager.get_transformer_lab_compatible_info()


@router.get("/python_libraries")
async def get_python_library_versions():
    """Get installed Python packages in JSON format"""
    try:
        packages = subprocess.check_output(
            sys.executable + " -m pip list --format=json", 
            shell=True
        )
        packages = packages.decode("utf-8")
        return json.loads(packages)
    except Exception as e:
        return {"error": f"Failed to get Python packages: {e}"}


@router.get("/pytorch_collect_env")
async def get_pytorch_collect_env():
    """Get PyTorch environment information"""
    try:
        output = subprocess.check_output(
            sys.executable + " -m torch.utils.collect_env", 
            shell=True
        )
        return output.decode("utf-8")
    except Exception as e:
        return f"Error getting PyTorch environment: {e}" 