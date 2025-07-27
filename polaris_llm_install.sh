#!/bin/bash
set -e

# 🌟 Polaris LLM Simple Installation Script (Fixed)

POLARIS_DIR="$HOME/.polarisllm"
POLARIS_API_DIR="${POLARIS_DIR}/polarisllm-api"
POLARIS_STUDIO_DIR="${POLARIS_DIR}/polarisllm-studio"
VENV_DIR="${POLARIS_DIR}/venv"
RUN_DIR=$(pwd)

##############################
# Helper Functions
##############################

err_report() {
  echo "Error on line $1"
}

trap 'err_report $LINENO' ERR

abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

if [[ -t 1 ]]
then
  tty_escape() { printf "\033[%sm" "$1"; }
else
  tty_escape() { :; }
fi
tty_mkbold() { tty_escape "1;$1"; }
tty_blue="$(tty_mkbold 34)"
tty_red="$(tty_mkbold 31)"
tty_bold="$(tty_mkbold 39)"
tty_reset="$(tty_escape 0)"

ohai() {
  printf "${tty_blue}==>${tty_bold} %s${tty_reset}\n" "$@"
}

warn() {
  printf "${tty_red}Warning${tty_reset}: %s\n" "$1" >&2
}

title() {
  echo ""
  printf "%s#########################################################################%s\n" "${tty_blue}" "${tty_reset}"
  printf "${tty_blue}#### ${tty_bold} %s${tty_reset}\n" "$@"
  printf "%s#########################################################################%s\n" "${tty_blue}" "${tty_reset}"
}

check_python() {
  if ! command -v python3 &> /dev/null; then
    abort "❌ Python3 is not installed. Please install Python 3.8+ and try again."
  else
    PYTHON_VERSION=$(python3 --version)
    ohai "✅ Python is installed: $PYTHON_VERSION"
  fi
}

check_node() {
  if ! command -v node &> /dev/null; then
    warn "Node.js is not installed. The studio app will not work without Node.js."
    return 1
  else
    NODE_VERSION=$(node --version)
    ohai "✅ Node.js is installed: $NODE_VERSION"
    return 0
  fi
}

check_npm() {
  if ! command -v npm &> /dev/null; then
    warn "npm is not installed. The studio app will not work without npm."
    return 1
  else
    NPM_VERSION=$(npm --version)
    ohai "✅ npm is installed: $NPM_VERSION"
    return 0
  fi
}

# Check OS
OS="$(uname)"
if [[ "${OS}" == "Linux" ]]
then
  POLARIS_ON_LINUX=1
elif [[ "${OS}" == "Darwin" ]]
then
  POLARIS_ON_MACOS=1
else
  abort "Polaris LLM is only supported on macOS and Linux, you are running ${OS}."
fi

##############################
## Step 1: Download Polaris LLM Components
##############################

download_polaris_llm() {
  title "Step 1: Download Polaris LLM API and Studio"
  echo "🌟 Step 1: START"

  if ! command -v curl &> /dev/null; then
    abort "❌ curl is not installed. Please install curl and try again."
  else
    ohai "✅ curl is installed."
  fi

  if ! command -v unzip &> /dev/null; then
    abort "❌ unzip is not installed. Please install unzip and try again."
  else
    ohai "✅ unzip is installed."
  fi

  mkdir -p "${POLARIS_DIR}"

  # Download Polaris API - FIXED URL AND EXTRACTION
  ohai "📡 Downloading Polaris LLM API..."
  POLARIS_API_URL="https://github.com/bigideaafrica/polarisllm-api/archive/refs/heads/main.zip"
  
  curl -L "${POLARIS_API_URL}" -o "${POLARIS_DIR}/polaris-api.zip"
  rm -rf "${POLARIS_API_DIR}"
  
  cd "${POLARIS_DIR}"
  unzip -q polaris-api.zip
  # Fixed: The actual folder name from the zip
  mv polarisllm-api-main "${POLARIS_API_DIR}"
  rm polaris-api.zip

  POLARIS_API_VERSION=$(date +"%Y.%m.%d")
  echo "v${POLARIS_API_VERSION}" > "${POLARIS_API_DIR}/LATEST_VERSION"
  ohai "✅ Polaris API downloaded to ${POLARIS_API_DIR}"

  # Download Polaris AI Studio
  ohai "🎨 Downloading Polaris AI Studio..."
  POLARIS_STUDIO_URL="https://github.com/bigideaafrica/polaris-ai-studio/archive/refs/heads/main.zip"
  
  # Check if the studio repo exists
  if curl -f -s -o /dev/null "${POLARIS_STUDIO_URL}"; then
    curl -L "${POLARIS_STUDIO_URL}" -o "${POLARIS_DIR}/polaris-studio.zip"
    rm -rf "${POLARIS_STUDIO_DIR}"
    
    unzip -q polaris-studio.zip
    mv polaris-ai-studio-main "${POLARIS_STUDIO_DIR}"
    rm polaris-studio.zip

    echo "v${POLARIS_API_VERSION}" > "${POLARIS_STUDIO_DIR}/LATEST_VERSION"
    ohai "✅ Polaris Studio downloaded to ${POLARIS_STUDIO_DIR}"
  else
    warn "Polaris AI Studio repository not found. Skipping studio installation."
    warn "Only the API will be available."
  fi

  cd "${RUN_DIR}"
  echo "🌟 Step 1: COMPLETE"
}

##############################
## Step 2: Create Python Virtual Environment
##############################

create_python_environment() {
  title "Step 2: Create Python Virtual Environment"
  echo "🌟 Step 2: START"

  check_python

  # Create virtual environment
  if [ -d "$VENV_DIR" ]; then
    ohai "✅ Virtual environment already exists at $VENV_DIR"
  else
    ohai "🔧 Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    ohai "✅ Virtual environment created at $VENV_DIR"
  fi

  # Activate virtual environment
  source "$VENV_DIR/bin/activate"
  
  # Upgrade pip
  pip install --upgrade pip
  
  echo "🌟 Step 2: COMPLETE"
}

##############################
## Step 3: Install Dependencies
##############################

install_dependencies() {
  title "Step 3: Install Dependencies"
  echo "🌟 Step 3: START"

  # Activate virtual environment
  source "$VENV_DIR/bin/activate"

  # Detect GPU type
  HAS_NVIDIA=false
  HAS_AMD=false

  if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null) || echo "Issue with NVIDIA SMI"
    if [ -n "$GPU_INFO" ]; then
      echo "NVIDIA GPU detected: $GPU_INFO"
      HAS_NVIDIA=true
    fi
  elif command -v rocminfo &> /dev/null; then
    echo "AMD GPU detected"
    HAS_AMD=true
  fi

  echo "HAS_NVIDIA=$HAS_NVIDIA, HAS_AMD=$HAS_AMD"

  # Install Python dependencies from API
  ohai "📦 Installing Polaris API Python dependencies..."
  cd "${POLARIS_API_DIR}"

  # Check if requirements.txt exists
  if [ -f "requirements.txt" ]; then
    ohai "Found requirements.txt, installing dependencies..."
    
    if [ "$HAS_NVIDIA" = true ]; then
      echo "Installing with CUDA support..."
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
      pip install -r requirements.txt
    elif [ "$HAS_AMD" = true ]; then
      echo "Installing with ROCm support..."
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
      pip install -r requirements.txt
    else
      echo "Installing CPU-only versions..."
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
      pip install -r requirements.txt
    fi
  else
    ohai "No requirements.txt found, installing basic dependencies..."
    
    if [ "$HAS_NVIDIA" = true ]; then
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
      pip install fastapi uvicorn psutil pynvml
    elif [ "$HAS_AMD" = true ]; then
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
      pip install fastapi uvicorn psutil pyrsmi
    else
      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
      pip install fastapi uvicorn psutil
    fi
  fi

  # Check if uvicorn is working
  if ! command -v uvicorn &> /dev/null; then
    abort "❌ Uvicorn installation failed."
  else
    ohai "✅ Python dependencies installed successfully."
  fi

  # Install Node.js dependencies for Studio (if exists)
  if [ -d "${POLARIS_STUDIO_DIR}" ]; then
    ohai "📦 Installing Polaris Studio Node.js dependencies..."
    cd "${POLARIS_STUDIO_DIR}"

    if check_node && check_npm; then
      if [ -f "package.json" ]; then
        echo "Installing npm dependencies..."
        npm install
        ohai "✅ Studio dependencies installed."
      else
        warn "No package.json found in Studio directory."
      fi
    else
      warn "Node.js/npm not available. Studio will not work until Node.js is installed."
    fi
  else
    warn "Studio directory not found. Only API will be available."
  fi

  cd "${RUN_DIR}"
  echo "🌟 Step 3: COMPLETE"
}

##############################
## Step 4: Create Startup Scripts
##############################

create_startup_scripts() {
  title "Step 4: Create Startup Scripts"
  
  # Create API startup script
  cat > "${POLARIS_DIR}/start_api.sh" << EOF
#!/bin/bash
# 🌟 Polaris API Startup Script

POLARIS_DIR="$HOME/.polarisllm"
VENV_DIR="\${POLARIS_DIR}/venv"
API_DIR="\${POLARIS_DIR}/polarisllm-api"

echo "🌟 Starting Polaris API..."

# Check if virtual environment exists
if [ ! -d "\$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at \$VENV_DIR"
    echo "Please run the installation script first."
    exit 1
fi

# Activate virtual environment
source "\$VENV_DIR/bin/activate"

# Change to API directory
cd "\$API_DIR"

# Find the main file
if [ -f "main.py" ]; then
    MAIN_FILE="main.py"
elif [ -f "app.py" ]; then
    MAIN_FILE="app.py"
elif [ -f "server.py" ]; then
    MAIN_FILE="server.py"
else
    echo "❌ No main Python file found (main.py, app.py, or server.py)"
    exit 1
fi

echo "🚀 Starting \$MAIN_FILE..."

# Start with nohup
nohup python "\$MAIN_FILE" > polaris_api.log 2>&1 &
API_PID=\$!

echo "✅ Polaris API started with PID: \$API_PID"
echo "📝 Logs: \${API_DIR}/polaris_api.log"
echo "🌐 URL: http://localhost:8339"
echo ""
echo "To stop: kill \$API_PID"
echo "To view logs: tail -f \${API_DIR}/polaris_api.log"
EOF

  # Create Studio startup script (only if studio exists)
  if [ -d "${POLARIS_STUDIO_DIR}" ]; then
    cat > "${POLARIS_DIR}/start_studio.sh" << EOF
#!/bin/bash
# 🎨 Polaris Studio Startup Script

POLARIS_DIR="$HOME/.polarisllm"
STUDIO_DIR="\${POLARIS_DIR}/polarisllm-studio"

echo "🎨 Starting Polaris Studio..."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js and try again."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

# Change to Studio directory
cd "\$STUDIO_DIR"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in \$STUDIO_DIR"
    exit 1
fi

# Start with npm
echo "🚀 Running npm start..."
npm start
EOF

    # Create combined startup script
    cat > "${POLARIS_DIR}/start_polaris.sh" << EOF
#!/bin/bash
# 🌟 Start both Polaris API and Studio

POLARIS_DIR="$HOME/.polarisllm"

echo "🌟 Starting Polaris LLM..."
echo ""

# Start API in background
echo "1. Starting API..."
"\${POLARIS_DIR}/start_api.sh"

# Wait a moment
sleep 3

echo ""
echo "2. Starting Studio..."
echo "   (This will run in foreground - press Ctrl+C to stop)"
echo ""

# Start Studio in foreground
"\${POLARIS_DIR}/start_studio.sh"
EOF

    chmod +x "${POLARIS_DIR}/start_studio.sh"
    chmod +x "${POLARIS_DIR}/start_polaris.sh"
  fi

  # Make scripts executable
  chmod +x "${POLARIS_DIR}/start_api.sh"
  
  ohai "✅ Startup scripts created:"
  echo "  🔧 API only:      ${POLARIS_DIR}/start_api.sh"
  if [ -d "${POLARIS_STUDIO_DIR}" ]; then
    echo "  🎨 Studio only:   ${POLARIS_DIR}/start_studio.sh"
    echo "  🌟 Both:          ${POLARIS_DIR}/start_polaris.sh"
  fi
}

##############################
## Utility Functions
##############################

start_polaris_api() {
  title "Starting Polaris API"
  source "$VENV_DIR/bin/activate"
  cd "${POLARIS_API_DIR}"
  
  # Find main file
  if [ -f "main.py" ]; then
    MAIN_FILE="main.py"
  elif [ -f "app.py" ]; then
    MAIN_FILE="app.py"
  elif [ -f "server.py" ]; then
    MAIN_FILE="server.py"
  else
    abort "❌ No main Python file found"
  fi
  
  echo "🚀 Starting Polaris API with nohup..."
  nohup python "$MAIN_FILE" > polaris_api.log 2>&1 &
  API_PID=$!
  echo "✅ Polaris API started with PID: $API_PID"
  echo "📝 Logs: ${POLARIS_API_DIR}/polaris_api.log"
  echo "🌐 URL: http://localhost:8339"
}

start_polaris_studio() {
  if [ ! -d "${POLARIS_STUDIO_DIR}" ]; then
    abort "❌ Studio not installed. Only API is available."
  fi
  
  title "Starting Polaris Studio"
  cd "${POLARIS_STUDIO_DIR}"
  
  if [ -f "package.json" ]; then
    echo "🚀 Starting Polaris Studio..."
    npm start
  else
    abort "❌ package.json not found in Studio directory."
  fi
}

doctor() {
  title "Polaris LLM Doctor"
  echo "🔍 System Check:"
  echo "OS: $(uname -s)"
  
  if command -v python3 &> /dev/null; then
    echo "✅ Python3: $(python3 --version)"
  else
    echo "❌ Python3: Not found"
  fi
  
  if [ -d "$VENV_DIR" ]; then
    echo "✅ Virtual Environment: $VENV_DIR"
    source "$VENV_DIR/bin/activate"
    echo "✅ Pip packages: $(pip list | wc -l) installed"
  else
    echo "❌ Virtual Environment: Not found"
  fi
  
  if [ -d "$POLARIS_API_DIR" ]; then
    echo "✅ API Directory: $POLARIS_API_DIR"
  else
    echo "❌ API Directory: Not found"
  fi
  
  if [ -d "$POLARIS_STUDIO_DIR" ]; then
    echo "✅ Studio Directory: $POLARIS_STUDIO_DIR"
  else
    echo "⚠️  Studio Directory: Not found (API-only mode)"
  fi
  
  if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
  else
    echo "❌ Node.js: Not found"
  fi
  
  if command -v npm &> /dev/null; then
    echo "✅ npm: $(npm --version)"
  else
    echo "❌ npm: Not found"
  fi
  
  if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU: Available"
  elif command -v rocminfo &> /dev/null; then
    echo "✅ AMD GPU: Available"
  else
    echo "ℹ️  GPU: CPU-only mode"
  fi
}

print_success_message() {
  title "🌟 Polaris LLM Installation Complete! 🌟"
  echo ""
  echo "📂 Installation Directory: ${POLARIS_DIR}"
  echo "🔧 API: ${POLARIS_API_DIR}"
  if [ -d "${POLARIS_STUDIO_DIR}" ]; then
    echo "🎨 Studio: ${POLARIS_STUDIO_DIR}"
  fi
  echo "🐍 Python Environment: ${VENV_DIR}"
  echo ""
  echo "🚀 Quick Start:"
  echo "  ${POLARIS_DIR}/start_api.sh        # Start API only"
  if [ -d "${POLARIS_STUDIO_DIR}" ]; then
    echo "  ${POLARIS_DIR}/start_studio.sh     # Start Studio only"  
    echo "  ${POLARIS_DIR}/start_polaris.sh    # Start both API and Studio"
  fi
  echo ""
  echo "🌐 URLs (after starting):"
  echo "  API:    http://localhost:8339"
  echo "  Docs:   http://localhost:8339/docs"
  if [ -d "${POLARIS_STUDIO_DIR}" ]; then
    echo "  Studio: http://localhost:3000 (typically)"
  fi
  echo ""
  echo "📝 Logs: ${POLARIS_API_DIR}/polaris_api.log"
  echo ""
}

# Main execution
if [[ "$#" -eq 0 ]]; then
  title "🌟 Polaris LLM Simple Installation (No Conda) 🌟"
  download_polaris_llm
  create_python_environment
  install_dependencies
  create_startup_scripts
  print_success_message
else
  case "$1" in
    download_polaris_llm)
      download_polaris_llm
      ;;
    create_python_environment)
      create_python_environment
      ;;
    install_dependencies)
      install_dependencies
      ;;
    create_startup_scripts)
      create_startup_scripts
      ;;
    start_api)
      start_polaris_api
      ;;
    start_studio)
      start_polaris_studio
      ;;
    doctor)
      doctor
      ;;
    *)
      echo "🌟 Polaris LLM Installation Script (Fixed)"
      echo ""
      echo "Available commands:"
      echo "  download_polaris_llm        - Download API and Studio"
      echo "  create_python_environment   - Create Python virtual environment"
      echo "  install_dependencies        - Install Python and Node.js dependencies"
      echo "  create_startup_scripts      - Create startup scripts"
      echo "  start_api                   - Start Polaris API"
      echo "  start_studio                - Start Polaris Studio"
      echo "  doctor                      - System diagnostics"
      echo ""
      echo "Or run without arguments for full installation."
      ;;
  esac
fi