#!/usr/bin/env python3
"""
🌟 Polaris System Detection API - Setup Script
Initial setup and dependency installation
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False


def main():
    """Run setup process"""
    print("🌟 ================================")
    print("🌟  POLARIS SETUP SCRIPT")
    print("🌟 ================================")
    
    print(f"🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        return False
    
    # Create virtual environment
    venv_path = Path("venv")
    if not venv_path.exists():
        print("🔧 Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv", "Virtual environment creation"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation command
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Upgrade pip
    run_command(f"{pip_cmd} install --upgrade pip", "Pip upgrade")
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Requirements installation"):
        print("⚠️  Some packages may have failed to install")
        print("   This is normal if you don't have GPU libraries available")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("🔧 Creating .env configuration file...")
        env_content = """# 🌟 Polaris System Detection API Configuration

# Server settings
POLARIS_HOST=0.0.0.0
POLARIS_PORT=8339
POLARIS_RELOAD=true

# Legacy compatibility (disabled by default)
POLARIS_LEGACY_COMPATIBLE=false
POLARIS_LEGACY_PORT=8338

# Feature toggles
POLARIS_ENABLE_GPU_DETECTION=true
POLARIS_ENABLE_MAC_SPECIFIC=true
POLARIS_ENABLE_REALTIME_MONITORING=true
"""
        env_file.write_text(env_content)
        print("   ✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    # Test installation
    print("🧪 Testing installation...")
    test_cmd = f"{python_cmd} -c \"from app.main import app; print('✅ Import successful')\""
    if run_command(test_cmd, "Import test"):
        print("🎉 Setup completed successfully!")
        print("\n🚀 Quick start:")
        print(f"   1. Activate virtual environment: {activate_cmd}")
        print("   2. Run: python main.py")
        print("   3. Open: http://localhost:8339")
        return True
    else:
        print("❌ Setup failed during testing")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 