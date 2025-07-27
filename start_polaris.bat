@echo off
REM 🌟 Polaris System Detection API Startup Script for Windows

echo 🌟 ================================
echo 🌟  POLARIS SYSTEM DETECTION API
echo 🌟 ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip and try again.
    pause
    exit /b 1
)

echo ✅ Python and pip detected

REM Check if virtual environment exists
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check system compatibility
echo 🔍 Checking system compatibility...
python -c "import platform; import torch; print(f'🖥️  OS: {platform.system()} {platform.release()}'); print(f'🐍 Python: {platform.python_version()}'); print(f'🔥 PyTorch: {torch.__version__}'); print(f'🎮 CUDA Available: {torch.version.cuda}' if torch.cuda.is_available() else '🍎 Apple MPS Available' if torch.backends.mps.is_available() else '💻 CPU-only mode')"

echo.
echo 🚀 Starting Polaris System Detection API...
echo 📊 Server will be available at: http://localhost:8339
echo 📖 API Documentation: http://localhost:8339/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python main.py

pause