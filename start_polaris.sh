#!/bin/bash

# 🌟 Polaris System Detection API Startup Script

echo "🌟 ================================"
echo "🌟  POLARIS SYSTEM DETECTION API"
echo "🌟 ================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip and try again."
    exit 1
fi

echo "✅ Python and pip detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check system compatibility
echo "🔍 Checking system compatibility..."
python3 -c "
import platform
import torch
print(f'🖥️  OS: {platform.system()} {platform.release()}')
print(f'🐍 Python: {platform.python_version()}')
print(f'🔥 PyTorch: {torch.__version__}')

if torch.cuda.is_available():
    print(f'🎮 CUDA Available: {torch.version.cuda}')
elif torch.backends.mps.is_available():
    print('🍎 Apple MPS Available')
else:
    print('💻 CPU-only mode')
"

echo ""
echo "🚀 Starting Polaris System Detection API..."
echo "📊 Server will be available at: http://localhost:8339"
echo "📖 API Documentation: http://localhost:8339/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 main.py