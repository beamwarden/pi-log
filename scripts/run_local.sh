#!/usr/bin/env bash
set -euo pipefail

# Ensure we're in the repo root
cd "$(dirname "$0")/.."

# Ensure config exists
if [ ! -f config.toml ]; then
    echo "config.toml not found. Copy config.toml.example and edit it."
    exit 1
fi

# Activate venv if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Extract values from config.toml
DEVICE=$(grep '^device' config.toml | cut -d '=' -f2 | tr -d ' "')
BAUDRATE=$(grep '^baudrate' config.toml | cut -d '=' -f2 | tr -d ' "')
DB=$(grep '^db_path' config.toml | cut -d '=' -f2 | tr -d ' "')
API_URL=$(grep '^endpoint' config.toml | cut -d '=' -f2 | tr -d ' "')
API_TOKEN=$(grep '^api_token' config.toml | cut -d '=' -f2 | tr -d ' "')
DEVICE_ID=$(grep '^node_id' config.toml | cut -d '=' -f2 | tr -d ' "')

# Run the ingestion agent via run.py
python run.py \
    --device "$DEVICE" \
    --baudrate "$BAUDRATE" \
    --device-type mightyohm \
    --db "$DB" \
    --api-url "$API_URL" \
    --api-token "$API_TOKEN" \
    --device-id "$DEVICE_ID"
