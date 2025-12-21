#!/usr/bin/env bash
set -euo pipefail

echo "[pi-setup] Starting Raspberry Pi ingestion environment setup..."

# Ensure script is run on a Pi-like environment
if ! uname -a | grep -qi "arm"; then
    echo "[pi-setup] Warning: This does not appear to be a Raspberry Pi."
fi

# Ensure Python exists
if ! command -v python3 >/dev/null 2>&1; then
    echo "[pi-setup] Python3 not found. Please install Python 3.9+."
    exit 1
fi

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    echo "[pi-setup] Creating virtual environment..."
    python3 -m venv venv
fi

echo "[pi-setup] Activating virtual environment..."
# shellcheck disable=SC1091
source venv/bin/activate

echo "[pi-setup] Upgrading pip..."
pip install --upgrade pip

echo "[pi-setup] Installing required Python packages..."
pip install -r requirements.txt

# Create logs directory if missing
if [ ! -d "logs" ]; then
    echo "[pi-setup] Creating logs directory..."
    mkdir -p logs
fi

echo "[pi-setup] Setup complete."
echo "[pi-setup] You can now run the ingestion loop with:"
echo "           source venv/bin/activate && python -m app.ingestion_loop"
