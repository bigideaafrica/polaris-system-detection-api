#!/bin/bash
set -e

# 🌟 Polaris LLM Installation Script
# Based on Transformer Lab's install.sh but customized for Polaris LLM

ENV_NAME="polarisllm"
POLARIS_DIR="$HOME/.polarisllm"
POLARIS_API_DIR="${POLARIS_DIR}/polarisllm-api"
POLARIS_STUDIO_DIR="${POLARIS_DIR}/polarisllm-studio"

MINIFORGE_ROOT=${POLARIS_DIR}/miniforge3
CONDA_BIN=${MINIFORGE_ROOT}/bin/conda
MAMBA_BIN=${MINIFORGE_ROOT}/bin/mamba
ENV_DIR=${POLARIS_DIR}/envs/${ENV_NAME}
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
tty_underline="$(tty_escape "4;39")"
tty_blue="$(tty_mkbold 34)"
tty_red="$(tty_mkbold 31)"
tty_bold="$(tty_mkbold 39)"
tty_reset="$(tty_escape 0)"

shell_join() {
  local arg
  printf "%s" "$1"
  shift
  for arg in "$@"
  do
    printf " "
    printf "%s" "${arg// /\ }"
  done
}

chomp() {
  printf "%s" "${1/"$'\n'"/}"
}

ohai() {
  printf "${tty_blue}==>${tty_bold} %s${tty_reset}\n" "$(shell_join "$@")"
}

warn() {
  printf "${tty_red}Warning${tty_reset}: %s\n" "$(chomp "$1")" >&2
}

title() {
  echo ""
  printf "%s#########################################################################%s\n" "${tty_blue}" "${tty_reset}"
  printf "${tty_blue}#### ${tty_bold} %s${tty_reset}\n" "$(shell_join "$@")"
  printf "%s#########################################################################%s\n" "${tty_blue}" "${tty_reset}"
}

check_conda() {
  if ! command -v "${CONDA_BIN}" &> /dev/null; then
    abort "❌ Conda is not installed at ${MINIFORGE_ROOT}. Please install Conda using '${POLARIS_DIR}/polarisllm-api/install.sh install_conda' and try again."
  else
    ohai "✅ Conda is installed at ${MINIFORGE_ROOT}."
  fi
}

check_mamba() {
  if ! command -v "${MAMBA_BIN}" &> /dev/null; then
    abort "❌ Mamba is not installed at ${MINIFORGE_ROOT}. Please install Mamba using '${POLARIS_DIR}/polarisllm-api/install.sh install_conda' and try again."
  else
    ohai "✅ Mamba is installed at ${MINIFORGE_ROOT}."
  fi
}

check_python() {
  if ! command -v python &> /dev/null; then
    abort "❌ Python is not installed as 'python'. Please install Python and try again or it could be installed as 'python3'"
  else
    # store python version in variable:
    PYTHON_VERSION=$(python --version)
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

unset_conda_for_sure() {
  { conda deactivate && conda deactivate && conda deactivate; } 2> /dev/null
  { mamba deactivate && mamba deactivate && mamba deactivate; } 2> /dev/null
  export PYTHONNOUSERSITE=1
  unset PYTHONPATH
  unset PYTHONHOME
}

check_if_conda_envronments_dot_text_is_writable() {
  if [ -f "$HOME/.conda/environments.txt" ]; then
    if [ -w "$HOME/.conda/environments.txt" ]; then
      echo -n
    else
      abort "❌ The file $HOME/.conda/environments.txt exists but is not writable. Please run [sudo chown -R \$USER ~/.conda] in the terminal to fix conda permissions."
    fi
  else
    echo -n
  fi
}

# First check OS.
OS="$(uname)"
KERNEL=$(uname -r)
if [[ "${OS}" == "Linux" ]]
then
  POLARIS_ON_LINUX=1
elif [[ "${OS}" == "Darwin" ]]
then
  POLARIS_ON_MACOS=1
else
  abort "Polaris LLM is only supported on macOS and Linux, you are running ${OS}."
fi

# Check for WSL
if [[ "${KERNEL}" =~ ([Mm]icrosoft|[Ww][Ss][Ll]2) ]]; then
  POLARIS_ON_WSL=1
else
  POLARIS_ON_WSL=0
fi

##############################
## Step 1: Download Polaris LLM Components
##############################

download_polaris_llm() {
  title "Step 1: Download Polaris LLM API and Studio"
  echo "🌟 Step 1: START"

  # First check that curl is installed:
  if ! command -v curl &> /dev/null; then
    abort "❌ curl is not installed on the remote host. Please install curl and try again."
  else
    ohai "✅ curl is installed."
  fi

  # Create the Polaris directory
  mkdir -p "${POLARIS_DIR}"

  # Download Polaris API
  ohai "📡 Downloading Polaris System Detection API..."
  POLARIS_API_URL="https://github.com/bigideaafrica/polaris-system-detection-api/archive/refs/heads/main.zip"
  echo "Download Location: $POLARIS_API_URL"

  curl -L "${POLARIS_API_URL}" -o "${POLARIS_DIR}/polaris-api.zip"
  rm -rf "${POLARIS_API_DIR}"
  
  # Extract and rename
  cd "${POLARIS_DIR}"
  unzip -q polaris-api.zip
  mv polaris-system-detection-api-main "${POLARIS_API_DIR}"
  rm polaris-api.zip

  # Get the latest version from the API repo (create a version file)
  POLARIS_API_VERSION=$(date +"%Y.%m.%d")
  echo "v${POLARIS_API_VERSION}" > "${POLARIS_API_DIR}/LATEST_VERSION"

  ohai "✅ Polaris API downloaded to ${POLARIS_API_DIR}"

  # Download Polaris AI Studio
  ohai "🎨 Downloading Polaris AI Studio..."
  POLARIS_STUDIO_URL="https://github.com/bigideaafrica/polaris-ai-studio/archive/refs/heads/main.zip"
  echo "Download Location: $POLARIS_STUDIO_URL"

  curl -L "${POLARIS_STUDIO_URL}" -o "${POLARIS_DIR}/polaris-studio.zip"
  rm -rf "${POLARIS_STUDIO_DIR}"
  
  # Extract and rename
  unzip -q polaris-studio.zip
  mv polaris-ai-studio-main "${POLARIS_STUDIO_DIR}"
  rm polaris-studio.zip

  # Create version file for studio
  echo "v${POLARIS_API_VERSION}" > "${POLARIS_STUDIO_DIR}/LATEST_VERSION"

  ohai "✅ Polaris Studio downloaded to ${POLARIS_STUDIO_DIR}"

  cd "${RUN_DIR}"
  echo "🌟 Step 1: COMPLETE"
}

##############################
## Step 2: Install Conda
##############################

install_conda() {
  title "Step 2: Install Conda for Polaris LLM"
  echo "🌟 Step 2: START"

  unset_conda_for_sure

  # check if conda already exists:
  if ! command -v "${CONDA_BIN}" &> /dev/null; then
    echo "Conda is not installed at ${MINIFORGE_ROOT}."
    OS=$(uname -s)
    ARCH=$(uname -m)

    if [ "$OS" == "Darwin" ]; then
        OS="MacOSX"
    fi

    MINIFORGE_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$OS-$ARCH.sh"
    echo Downloading "$MINIFORGE_URL"

    # Change the directory to the Polaris directory
    mkdir -p "$POLARIS_DIR"
    cd "$POLARIS_DIR"
    # first check if the MINIFORGE_ROOT exists, and if so, delete it:
    if [ -d "$MINIFORGE_ROOT" ]; then
      echo "Deleting existing Miniforge installation at $MINIFORGE_ROOT"
      rm -rf "$MINIFORGE_ROOT"
    fi
    curl -L -o miniforge_installer.sh "$MINIFORGE_URL" && bash miniforge_installer.sh -b -p "$MINIFORGE_ROOT" && rm miniforge_installer.sh
  else
      ohai "Conda is installed at ${MINIFORGE_ROOT}, we do not need to install it"
  fi

  # Enable conda in shell
  eval "$(${CONDA_BIN} shell.bash hook)"

  check_conda
  check_mamba

  conda info
  
  cd "${RUN_DIR}"
  echo "🌟 Step 2: COMPLETE"
}

##############################
## Step 3: Create the Conda Environment
##############################

create_conda_environment() {
  title "Step 3: Create the Polaris LLM Conda Environment"
  echo "🌟 Step 3: START"

  check_if_conda_envronments_dot_text_is_writable

  check_conda

  unset_conda_for_sure

  eval "$(${CONDA_BIN} shell.bash hook)"

  conda info --envs

  # Create the conda environment for Polaris LLM
  if { conda env list | grep "$ENV_DIR"; } >/dev/null 2>&1; then
      echo "✅ Conda environment $ENV_DIR already exists."
  else
      echo mamba create -y -n "$ENV_DIR" python=3.11
      conda create -y -k --prefix "$ENV_DIR" python=3.11
  fi

  # Activate the newly created environment
  echo conda activate "$ENV_DIR"
  conda activate "$ENV_DIR"
  echo "🌟 Step 3: COMPLETE"
}

##############################
## Step 4: Install Dependencies
##############################

install_dependencies() {
  title "Step 4: Install Dependencies for Polaris LLM"
  echo "Warning: this step may take a while to complete the first time."
  echo "In this step, all Python and Node.js dependencies will be installed."
  echo "🌟 Step 4: START"

  unset_conda_for_sure
  eval "$(${CONDA_BIN} shell.bash hook)"
  conda activate "$ENV_DIR"

  check_python

  # Detect GPU type: NVIDIA vs AMD (ROCm)
  HAS_NVIDIA=false
  HAS_AMD=false

  if command -v nvidia-smi &> /dev/null; then
      echo "nvidia-smi is available"
      GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits) || echo "Issue with NVIDIA SMI"
      if [ -n "$GPU_INFO" ]; then
          echo "NVIDIA GPU detected: $GPU_INFO"
          HAS_NVIDIA=true
      else
          echo "nvidia-smi exists but no NVIDIA GPU found"
      fi
  elif command -v rocminfo &> /dev/null; then
      echo "rocminfo is available"
      HAS_AMD=true
  fi

  # Install uv for faster Python package installation
  pip install uv
  
  echo "HAS_NVIDIA=$HAS_NVIDIA, HAS_AMD=$HAS_AMD"
  PIP_WHEEL_FLAGS="--upgrade"

  # Install Python dependencies from API
  ohai "📦 Installing Polaris API Python dependencies..."
  cd "${POLARIS_API_DIR}"

  if [ "$HAS_NVIDIA" = true ]; then
      echo "Your computer has a GPU; installing CUDA support:"
      conda install -y cuda==12.8.1 --force-reinstall -c nvidia/label/cuda-12.8.1

      if [ -e "requirements.txt" ]; then
        REQS_PATH="requirements.txt"
      else
        echo "Error: requirements.txt not found in API directory."
        exit 1
      fi

      PIP_WHEEL_FLAGS+=" --index https://download.pytorch.org/whl/cu128"
      uv pip install ${PIP_WHEEL_FLAGS} -r ${REQS_PATH}

  elif [ "$HAS_AMD" = true ]; then
      echo "Installing requirements for ROCm:"
      if [ -e "requirements-rocm.txt" ]; then
        REQS_PATH="requirements-rocm.txt"
      elif [ -e "requirements.txt" ]; then
        REQS_PATH="requirements.txt"
      else
        echo "Error: requirements file not found in API directory."
        exit 1
      fi

      PIP_WHEEL_FLAGS+=" --index https://download.pytorch.org/whl/rocm6.3"
      uv pip install ${PIP_WHEEL_FLAGS} -r ${REQS_PATH}

      if [ "$POLARIS_ON_WSL" = 1 ]; then
        location=$(pip show torch | grep Location | awk -F ": " '{print $2}')
        cd "${location}/torch/lib/" || exit 1
        rm -f libhsa-runtime64.so*
        cp /opt/rocm/lib/libhsa-runtime64.so.1.14.0 .
        ln -sf libhsa-runtime64.so.1.14.0 libhsa-runtime64.so.1
        ln -sf libhsa-runtime64.so.1 libhsa-runtime64.so
      fi

  else
      echo "No GPU detected. Installing CPU-only versions."

      if [ -e "requirements-cpu.txt" ]; then
        REQS_PATH="requirements-cpu.txt"
      elif [ -e "requirements.txt" ]; then
        REQS_PATH="requirements.txt"
      else
        echo "Error: requirements file not found in API directory."
        exit 1
      fi

      if [[ -z "${POLARIS_ON_MACOS}" ]]; then
          PIP_WHEEL_FLAGS+=" --index https://download.pytorch.org/whl/cpu"
      fi

      uv pip install ${PIP_WHEEL_FLAGS} -r ${REQS_PATH}
  fi

  # Check if uvicorn is working
  if ! command -v uvicorn &> /dev/null; then
    abort "❌ Uvicorn is not installed. Python dependencies installation failed."
  else
    ohai "✅ Uvicorn is installed."
  fi

  # Install Node.js dependencies for Studio
  ohai "📦 Installing Polaris Studio Node.js dependencies..."
  cd "${POLARIS_STUDIO_DIR}"

  if check_node && check_npm; then
    echo "Installing npm dependencies..."
    npm install
    ohai "✅ Studio dependencies installed."
  else
    warn "Node.js/npm not available. Studio will not work until Node.js is installed."
  fi

  # Record the status after this install
  cd "${POLARIS_API_DIR}"
  PIP_LIST=$(pip list --format json)
  echo "${PIP_LIST}" > "${POLARIS_API_DIR}/INSTALLED_DEPENDENCIES"

  cd "${RUN_DIR}"
  echo "🌟 Step 4: COMPLETE"
}

##############################
## Additional Helper Functions
##############################

list_installed_packages() {
  unset_conda_for_sure
  eval "$(${CONDA_BIN} shell.bash hook)"
  conda activate "${ENV_DIR}"
  pip list --format json
}

list_environments() {
  check_if_conda_envronments_dot_text_is_writable
  unset_conda_for_sure
  eval "$(${CONDA_BIN} shell.bash hook)"
  conda env list
}

doctor() {
  title "Polaris LLM Doctor"
  ohai "Checking if everything is installed correctly."
  echo "Your machine is: $OS"
  echo "Your shell is: $SHELL"

  if command -v "${CONDA_BIN}" &> /dev/null; then
    echo "Your conda version is: $(${CONDA_BIN} --version)" || echo "Issue with conda"
    echo "Conda is seen in path at: $(which conda)" || echo "Conda is not in your path"
  else
    echo "Conda is not installed at ${MINIFORGE_ROOT}."
  fi

  if command -v nvidia-smi &> /dev/null; then
    echo "Your nvidia-smi version is: $(nvidia-smi --version)"
  else
    echo "nvidia-smi is not installed."
  fi

  if check_node && check_npm; then
    echo "Node.js and npm are properly installed."
  else
    echo "Node.js/npm issues detected."
  fi

  check_conda
  check_python
}

start_polaris_api() {
  title "Starting Polaris API"
  
  unset_conda_for_sure
  eval "$(${CONDA_BIN} shell.bash hook)"
  conda activate "$ENV_DIR"
  
  cd "${POLARIS_API_DIR}"
  
  if [ -f "main.py" ]; then
    echo "🚀 Starting Polaris API with nohup..."
    nohup python main.py > polaris_api.log 2>&1 &
    API_PID=$!
    echo "✅ Polaris API started with PID: $API_PID"
    echo "📝 Logs are being written to: ${POLARIS_API_DIR}/polaris_api.log"
    echo "🌐 API should be available at: http://localhost:8339"
  else
    echo "❌ main.py not found in API directory."
    exit 1
  fi
}

start_polaris_studio() {
  title "Starting Polaris Studio"
  
  cd "${POLARIS_STUDIO_DIR}"
  
  if [ -f "package.json" ]; then
    echo "🚀 Starting Polaris Studio..."
    npm start
  else
    echo "❌ package.json not found in Studio directory."
    exit 1
  fi
}

create_startup_scripts() {
  title "Creating Startup Scripts"
  
  # Create API startup script
  cat > "${POLARIS_DIR}/start_api.sh" << 'EOF'
#!/bin/bash
# 🌟 Polaris API Startup Script

POLARIS_DIR="$HOME/.polarisllm"
ENV_DIR="${POLARIS_DIR}/envs/polarisllm"
CONDA_BIN="${POLARIS_DIR}/miniforge3/bin/conda"
API_DIR="${POLARIS_DIR}/polarisllm-api"

echo "🌟 Starting Polaris API..."

# Activate conda environment
eval "$(${CONDA_BIN} shell.bash hook)"
conda activate "$ENV_DIR"

# Change to API directory
cd "$API_DIR"

# Start with nohup
nohup python main.py > polaris_api.log 2>&1 &
API_PID=$!

echo "✅ Polaris API started with PID: $API_PID"
echo "📝 Logs: ${API_DIR}/polaris_api.log"
echo "🌐 URL: http://localhost:8339"
EOF

  # Create Studio startup script
  cat > "${POLARIS_DIR}/start_studio.sh" << 'EOF'
#!/bin/bash
# 🎨 Polaris Studio Startup Script

POLARIS_DIR="$HOME/.polarisllm"
STUDIO_DIR="${POLARIS_DIR}/polarisllm-studio"

echo "🎨 Starting Polaris Studio..."

# Change to Studio directory
cd "$STUDIO_DIR"

# Start with npm
npm start
EOF

  # Make scripts executable
  chmod +x "${POLARIS_DIR}/start_api.sh"
  chmod +x "${POLARIS_DIR}/start_studio.sh"
  
  ohai "✅ Startup scripts created:"
  echo "  API: ${POLARIS_DIR}/start_api.sh"
  echo "  Studio: ${POLARIS_DIR}/start_studio.sh"
}

print_success_message() {
  title "🌟 Polaris LLM Installation Complete! 🌟"
  echo "------------------------------------------"
  echo "Polaris LLM is installed to:"
  echo "  ${POLARIS_DIR}"
  echo ""
  echo "Components installed:"
  echo "  🔧 API: ${POLARIS_API_DIR}"
  echo "  🎨 Studio: ${POLARIS_STUDIO_DIR}"
  echo ""
  echo "Your conda environment:"
  echo "  📦 ${ENV_DIR}"
  echo ""
  echo "🚀 Quick Start Commands:"
  echo "  Start API:    ${POLARIS_DIR}/start_api.sh"
  echo "  Start Studio: ${POLARIS_DIR}/start_studio.sh"
  echo ""
  echo "🌐 URLs (after starting):"
  echo "  API:    http://localhost:8339"
  echo "  Studio: http://localhost:3000 (typically)"
  echo "------------------------------------------"
  echo ""
}

# Check if there are arguments to this script
if [[ "$#" -eq 0 ]]; then
  title "🌟 Performing a full installation of Polaris LLM 🌟"
  download_polaris_llm
  install_conda
  create_conda_environment
  install_dependencies
  create_startup_scripts
  print_success_message
else
  for arg in "$@"
  do
    case $arg in
      download_polaris_llm)
        download_polaris_llm
        ;;
      install_conda)
        install_conda
        ;;
      create_conda_environment)
        create_conda_environment
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
      list_installed_packages)
        list_installed_packages
        ;;
      list_environments)
        list_environments
        ;;
      *)
        echo "🌟 Polaris LLM Installation Script"
        echo ""
        echo "Available commands:"
        echo "  download_polaris_llm     - Download API and Studio"
        echo "  install_conda           - Install Conda to ~/.polarisllm/miniforge3"
        echo "  create_conda_environment - Create polarisllm environment"
        echo "  install_dependencies    - Install Python and Node.js dependencies"
        echo "  create_startup_scripts  - Create startup scripts"
        echo "  start_api              - Start Polaris API with nohup"
        echo "  start_studio           - Start Polaris Studio with npm"
        echo "  doctor                 - System diagnostics"
        echo "  list_installed_packages - List Python packages"
        echo "  list_environments      - List conda environments"
        echo ""
        echo "Or run without arguments for full installation."
        abort "❌ Unknown argument: $arg"
        ;;
    esac
  done
fi