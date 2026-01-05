# Polymarket Reports

Generate and store Polymarket market snapshots as CSV files in the `reports/` folder.

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
