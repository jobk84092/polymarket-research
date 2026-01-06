#!/usr/bin/env zsh
set -euo pipefail

# Resolve workspace root relative to this script
SCRIPT_DIR=$(cd -- "$(dirname "$0")" >/dev/null 2>&1; pwd -P)
WORKSPACE=$(cd "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd -P)
cd "$WORKSPACE"

# Ensure output folder exists
mkdir -p reports

# Pass-through any optional args to select report types
# Examples:
#   ./scripts/run_reports_once.sh --top50
#   ./scripts/run_reports_once.sh --all-active
#   ./scripts/run_reports_once.sh --limit 100
python3 run_reports.py --outdir reports "$@"
