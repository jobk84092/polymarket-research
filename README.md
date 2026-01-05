# Polymarket Reports

Generate and store Polymarket market snapshots as CSV files in the `reports/` folder.

## Setup

It's best to use a Python virtual environment to avoid Conda/Homebrew conflicts:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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

## Notes

- These scripts call Polymarket's public Gamma API and save full JSON fields like `outcomes` and `outcomePrices` into CSVs.
- Use one Python interpreter consistently. If Conda is active, use Conda's `python`; if not, use `/usr/local/bin/python3` or the `.venv` interpreter.
