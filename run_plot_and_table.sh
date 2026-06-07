#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TOTAL_STEPS=12

if [ ! -d ".venv" ]; then
  echo "[0/${TOTAL_STEPS}] .venv not found. Please create the virtual environment first."
  exit 1
fi

echo "[1/${TOTAL_STEPS}] Activating virtual environment..."
source .venv/bin/activate

echo "[2/${TOTAL_STEPS}] Installing required packages..."
python -m pip install -r requirements.txt

run_step() {
  local step_label="$1"
  local step_dir="$2"
  local step_script="$3"

  echo "[$step_label] Running $step_script in $step_dir..."
  pushd "$SCRIPT_DIR/$step_dir" >/dev/null
  python "./$step_script"
  popd >/dev/null
  echo "[$step_label] Finished $step_script"
}

run_step "3/${TOTAL_STEPS}" "plot and table data/attack success rate" "draw attack success rate.py"
run_step "4/${TOTAL_STEPS}" "plot and table data/collateral impact" "draw collateral impact.py"
run_step "5/${TOTAL_STEPS}" "plot and table data/limit attack cost" "draw limit attack cost 33-165.py"
run_step "6/${TOTAL_STEPS}" "plot and table data/noise" "draw noise.py"
run_step "7/${TOTAL_STEPS}" "plot and table data/number of paper" "draw number of paper.py"
run_step "8/${TOTAL_STEPS}" "plot and table data/size attack overhead" "draw types attack overhead in one pic.py"
run_step "9/${TOTAL_STEPS}" "plot and table data/success rate over time" "draw rate over time.py"
run_step "10/${TOTAL_STEPS}" "plot and table data/Table AS size p2c infer" "cal AS size p2c infer.py"
run_step "11/${TOTAL_STEPS}" "plot and table data/total attack overhead" "draw total attack overhead.py"
run_step "12/${TOTAL_STEPS}" "plot and table data/transit degree" "draw TG.py"

echo "[done] Deactivating virtual environment..."
deactivate