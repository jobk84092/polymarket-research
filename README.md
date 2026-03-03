# Polymarket Reports

Generate and store Polymarket market snapshots as CSV files in the `reports/` folder.

## Repository Structure

Quick map of all key files so you can jump straight to what you need:

| File / Folder | What it does |
|---|---|
| `Polymarket.py` | Fetches **all active markets** from the Gamma API and saves a CSV snapshot |
| `top 50 polymarket.py` | Fetches the **top 50 markets by 24 h volume** and saves a CSV snapshot |
| `run_reports.py` | Orchestrator – runs either or both of the above; accepts CLI flags (`--top50`, `--all-active`, `--outdir`, `--limit`) |
| `review_latest.py` | **Review tool** – reads the latest CSV snapshots and prints a formatted table + summary; supports `--fetch`, `--export`, `--rows`, `--report` |
| `polymarket_alerts.py` | Polls for **YES-price moves** and sends Telegram notifications; runs continuously or in single-shot mode (`--once`) |
| `config.json` | Default settings (`limit`, `outdir`); CLI flags in `run_reports.py` override these |
| `pm_state.json` | Persisted price state used by `polymarket_alerts.py` to detect moves between cycles |
| `requirements.txt` | Python dependencies – install with `pip install -r requirements.txt` |
| `reports/` | Output folder: dated sub-folders (`YYYY-MM-DD/`), `latest_*` symlinks, and `rolling/` time-series files |
| `notebooks/analysis.ipynb` | Jupyter notebook with quick charts and summaries built on the CSVs in `reports/` |
| `scripts/run_daily_reports.sh` | Shell script to generate one snapshot per day (use with cron / launchd) |
| `scripts/run_reports_once.sh` | Shell script for a quick one-off run (same flags as `run_reports.py`) |
| `.github/workflows/reports.yml` | GitHub Actions workflow – runs weekly and uploads CSVs as artifacts |
| `.github/workflows/alerts.yml` | GitHub Actions workflow – runs every 10 minutes and sends Telegram alerts |
| `prompts/` | AI prompt files used for analysis and reporting (Cursor / ChatGPT) |
| `checks/validation_checklist.md` | Checklist to validate data, SQL, and report outputs |
| `sql/00_sources.md` | Documents source systems and assumptions for any SQL work |
| `DATA_LINEAGE.md` | Template for tracking data origins, transformations, and outputs |
| `AI_RULES.md` | Guardrails and quality standards for AI-assisted work in this repo |

## Setup

It's best to use a Python virtual environment to avoid Conda/Homebrew conflicts:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
Optional developer tooling (formatting/lint):

```bash
pip install pre-commit black ruff
pre-commit install
```

```

## Review the Latest CSV

Once reports have been generated, inspect them directly in the terminal:

```bash
# Show top markets by 24h volume (default, 20 rows)
python review_latest.py

# Show all active markets
python review_latest.py --report all

# Show both reports
python review_latest.py --report both

# Show more rows
python review_latest.py --rows 50

# Fetch fresh data from the API first, then review
python review_latest.py --fetch

# Also export a plain (uncompressed) CSV to reports/ for opening in Excel / Google Sheets
python review_latest.py --export
```

The script prints a summary header (snapshot time, market count, total 24h volume, total
liquidity) followed by a formatted table sorted by 24h volume.

- `--export` writes `reports/review_top.csv` or `reports/review_all.csv`
  (these are gitignored and won't be committed).

## On-Demand Usage

Run both reports (Top 50 24h volume and All Active markets):

```bash
python run_reports.py
```

Only Top 50 by 24h volume:

```bash
python run_reports.py --top50
```

Only All Active markets:

```bash
python run_reports.py --all-active
```

Choose output directory and limit:

```bash
python run_reports.py --outdir reports --limit 100
```

CSV files will be written to `reports/` with a UTC timestamp in the filename, for example:

- `reports/top_markets_24h_20260105T163000Z.csv`
- `reports/all_active_markets_20260105T163000Z.csv`

## Share With a Colleague

Your colleague can clone or download the repo and run with any Python 3.10+ environment. Recommended path is a virtual environment (cross-platform and avoids Conda/Homebrew conflicts):

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_reports.py
```

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_reports.py
```

If they prefer Conda, they can instead do:

```bash
conda create -n polymarket python=3.11 -y
conda activate polymarket
pip install -r requirements.txt
python run_reports.py
```

## Put This on GitHub

Initialize a local repo, commit, and push to GitHub (replace `YOUR_REPO_URL`):

```bash
git init
git add .
git commit -m "Initial commit: Polymarket reports"
git branch -M main
git remote add origin YOUR_REPO_URL
git push -u origin main
```

Notes:
- `.gitignore` keeps large/ephemeral files out of git (e.g., `reports/*.csv`, `.venv/`).
- `reports/.gitkeep` ensures the folder exists in the repo without committing CSVs.

## Scheduling (macOS)

Two simple options:

- Cron (ensure you use the full path to your Python):

```bash
crontab -e
# Run every 6 hours (adjust path to your workspace)
0 */6 * * * /usr/local/bin/python3 "/path/to/workspace/run_reports.py" >> "/path/to/workspace/reports/cron.log" 2>&1
```

- launchd (more mac-native). If you want, I can add a sample plist file.

## GitHub Actions (Weekly)

This repository includes a workflow at `.github/workflows/reports.yml` that runs once a week (Monday 00:00 UTC) and uploads the generated CSVs as build artifacts.

Trigger manually:

```bash
# From GitHub UI: Actions tab → Polymarket Reports Weekly → Run workflow
```

Artifacts can be downloaded from the workflow run page.

## Always-On (CI Alerts)

To keep alerts running even when your Mac is off, this repo includes a CI workflow that runs every 10 minutes and sends Telegram notifications if Secrets are set:

- Workflow: `.github/workflows/alerts.yml`
- Schedule: every 10 minutes (and manual trigger via Actions tab)
- Persists `pm_state.json` by committing it back to the repo after each run

Configure Secrets:

1. In GitHub → Repository → Settings → Secrets and variables → Actions
2. Add `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID`
3. The workflow will start sending alerts automatically

Note: CI runs are periodic (not continuous). For near real-time, consider deploying `polymarket_alerts.py` on a small cloud worker (e.g., Fly.io, Render, Railway) with env vars set.

## Configuration

- `config.json` controls defaults like `limit` and `outdir`:

```json
{
	"limit": 50,
	"outdir": "reports"
}
```

CLI flags in `run_reports.py` override config values.

## Outputs

- Partitioned by date: CSVs are saved under `reports/YYYY-MM-DD/`.
- Compressed: files are written as `.csv.gz` to save space.
- Latest pointers: `reports/latest_top_markets_24h.csv.gz` and `reports/latest_all_active_markets.csv.gz` always reflect the newest run.
- Rolling datasets: appended time-series in `reports/rolling/*.csv.gz`.
### Daily Polymarket Reports

To automatically generate one CSV per day for both all active markets and the top markets of the past 24 hours, use the provided script and a cron (or launchd) schedule.

Setup:
- Script: [scripts/run_daily_reports.sh](scripts/run_daily_reports.sh)
- Output: [reports/](reports) with daily partitions (YYYY-MM-DD), plus `latest_*` and `rolling/*` files.

Run once manually:
```bash
chmod +x scripts/run_daily_reports.sh
scripts/run_daily_reports.sh
```

Quick manual run on-demand:
```bash
chmod +x scripts/run_reports_once.sh
scripts/run_reports_once.sh          # runs both reports into reports/
scripts/run_reports_once.sh --top50  # only top 24h markets
scripts/run_reports_once.sh --all-active  # only all active markets
```

Schedule via cron (macOS/Linux):
```bash
crontab -e
# At 00:15 UTC daily (adjust to your preference)
15 0 * * * "/Users/jobkimani/Library/CloudStorage/OneDrive-Personal/JOB/personal stuff/learning centre/STATISTTICS/projects for practice/POLYMARKET/scripts/run_daily_reports.sh"
```

Optional: macOS LaunchAgent (copy into `~/Library/LaunchAgents/com.polymarket.reports.plist`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
	<dict>
		<key>Label</key>
		<string>com.polymarket.reports</string>
		<key>ProgramArguments</key>
		<array>
			<string>/bin/zsh</string>
			<string>-lc</string>
			<string>"/Users/jobkimani/Library/CloudStorage/OneDrive-Personal/JOB/personal stuff/learning centre/STATISTTICS/projects for practice/POLYMARKET/scripts/run_daily_reports.sh"</string>
		</array>
		<key>StartCalendarInterval</key>
		<dict>
			<key>Hour</key>
			<integer>0</integer>
			<key>Minute</key>
			<integer>15</integer>
		</dict>
		<key>StandardOutPath</key>
		<string>/Users/jobkimani/Library/CloudStorage/OneDrive-Personal/JOB/personal stuff/learning centre/STATISTTICS/projects for practice/POLYMARKET/reports/launchd.out.log</string>
		<key>StandardErrorPath</key>
		<string>/Users/jobkimani/Library/CloudStorage/OneDrive-Personal/JOB/personal stuff/learning centre/STATISTTICS/projects for practice/POLYMARKET/reports/launchd.err.log</string>
	</dict>
	</plist>
```
Load the agent:
```bash
launchctl load ~/Library/LaunchAgents/com.polymarket.reports.plist
```

This will produce exactly one snapshot per day per report (files include timestamps and are partitioned under the date directory).

## Notifications (Optional)

You can receive a Telegram message after runs:
- Local runs: set environment variables before executing:

```bash
export TELEGRAM_TOKEN="<bot_token>"
export TELEGRAM_CHAT_ID="<chat_id>"
python run_reports.py
- Alerts script (`polymarket_alerts.py`):
Configure once via a local `.env` (ignored by git):

```
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

Run with CLI flags:

```bash
python polymarket_alerts.py --poll-seconds 60 --top-n 50 --jump-points 0.08 --notify --cooldown-seconds 300
```

Notes:
- `--notify` controls whether Telegram messages are sent.
- The script logs a heartbeat each cycle and applies a cooldown per market to reduce noise.
```

- GitHub Actions: add `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` as repository Secrets (Settings → Secrets and variables → Actions). The weekly workflow will send a summary message if both are set.

Security note: never commit tokens to the repo. If a token is exposed, rotate it (create a new bot token) and remove the old one.

## Analysis Notebook

- See `notebooks/analysis.ipynb` for quick charts and summaries based on the latest and rolling CSVs.
- Install plotting deps:

```bash
pip install -r requirements.txt
```

- Open the notebook in VS Code or Jupyter and run all cells.

## Notes

- These scripts call Polymarket's public Gamma API and save full JSON fields like `outcomes` and `outcomePrices` into CSVs.
- Use one Python interpreter consistently. If Conda is active, use Conda's `python`; if not, use `/usr/local/bin/python3` or the `.venv` interpreter.
