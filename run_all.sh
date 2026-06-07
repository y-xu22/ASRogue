#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TOTAL_STEPS=6

echo "[1/${TOTAL_STEPS}] Creating virtual environment..."
python -m venv .venv
echo "[2/${TOTAL_STEPS}] Activating virtual environment..."
source .venv/bin/activate

echo "[3/${TOTAL_STEPS}] Installing required packages..."
python -m pip install -r requirements.txt

echo "[4/${TOTAL_STEPS}] Downloading dataset..."
python download.py https://publicdata.caida.org/datasets/as-relationships/serial-1/20241001.all-paths.bz2 -o data
echo "[5/${TOTAL_STEPS}] Running baseline inference..."
python run.py
echo "[6/${TOTAL_STEPS}] Running attack experiment..."
python run_multi.py allp2c allrand 10

echo "[done] Deactivating virtual environment..."
deactivate
