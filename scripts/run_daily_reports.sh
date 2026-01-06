#!/usr/bin/env zsh
set -euo pipefail

# Absolute workspace path (adjust if moved)
WORKSPACE="/Users/jobkimani/Library/CloudStorage/OneDrive-Personal/JOB/personal stuff/learning centre/STATISTTICS/projects for practice/POLYMARKET"
cd "$WORKSPACE"

# Ensure reports directory exists
mkdir -p reports

# Timestamp for logging
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG="reports/cron.log"

# Run both reports (Top 24h and All Active). Overrides outdir to reports/
{
  echo "[$TS] Starting daily Polymarket reports"
  python3 run_reports.py --outdir reports
  echo "[$TS] Completed daily Polymarket reports"
} >> "$LOG" 2>&1
