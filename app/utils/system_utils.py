"""
🌟 Polaris System Detection API - System Utilities
"""

import platform
import subprocess
import sys
from typing import Optional


def is_wsl() -> bool:
    """
    Detect if running on Windows Subsystem for Linux
    
    Returns:
        bool: True if running on WSL, False otherwise
    """
    # If we're on Windows, we're definitely not in WSL
    if platform.system() == "Windows":
        return False
    
    # Only try uname command on Unix-like systems
    try:
        kernel_output = subprocess.check_output(["uname", "-r"], text=True).lower()
        return "microsoft" in kernel_output or "wsl2" in kernel_output
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_platform_info() -> dict:
    """
    Get comprehensive platform information
    
    Returns:
        dict: Platform information including OS, architecture, etc.
    """
    return {
        "cpu": platform.machine(),
        "name": platform.node(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "os": platform.system(),
        "os_alias": platform.system_alias(
            platform.system(), 
            platform.release(), 
            platform.version()
        ),
        "is_wsl": is_wsl(),
    }


def safe_subprocess_run(command: str, shell: bool = True) -> Optional[str]:
    """
    Safely run a subprocess command with error handling
    
    Args:
        command: Command to run
        shell: Whether to run in shell mode
        
    Returns:
        str: Command output or None if failed
    """
    try:
        result = subprocess.check_output(command, shell=shell, text=True)
        return result.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️ Command failed: {command} - Error: {e}")
        return None


def bytes_to_string(data) -> str:
    """
    Convert bytes to string safely
    
    Args:
        data: Data to convert (bytes or string)
        
    Returns:
        str: Converted string
    """
    if isinstance(data, bytes):
        return data.decode(errors="ignore")
    return str(data) 