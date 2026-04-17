# Validation Checklist

## Data

- [ ] Raw snapshot CSV exists in `reports/YYYY-MM-DD/`
- [ ] `reports/latest_top_markets_24h.csv.gz` has been updated (check `snapshot_time` column)
- [ ] `reports/latest_all_active_markets.csv.gz` has been updated
- [ ] Rolling files (`reports/rolling/*.csv.gz`) are growing (row count increases each run)
- [ ] `snapshot_time` values are UTC ISO 8601 and match the expected run time
- [ ] `market_id` column contains integers (no nulls, no string IDs)
- [ ] `volume24hr` and `volume_total` are non-negative floats
- [ ] `outcomePrices` values parse as valid JSON lists of numbers in [0, 1]

## API

- [ ] `Polymarket.py` runs without errors: `python Polymarket.py`
- [ ] `top 50 polymarket.py` runs without errors
- [ ] `run_reports.py` runs end-to-end: `python run_reports.py --limit 10`
- [ ] HTTP response status is 200; no 429 rate-limit errors in output

## Alerts

- [ ] `polymarket_alerts.py --once` completes one cycle without errors
- [ ] `pm_state.json` is updated after a cycle run
- [ ] Telegram test message received (if `--notify` flag used with valid secrets)

## Reporting

- [ ] `python review_latest.py` prints a summary without errors
- [ ] `python review_latest.py --export` writes `reports/review_top.csv`
- [ ] `notebooks/analysis.ipynb` runs all cells without errors (after running reports once)

## SQL / Queries

- [ ] Source assumptions documented in `sql/00_sources.md`
- [ ] Any custom DuckDB / pandas query tested against the latest snapshot

## Evidence

- [ ] Supporting screenshots saved in `evidence/screenshots` (if applicable)
- [ ] Export artifacts saved in `evidence/exports` (if applicable)
- [ ] Execution logs saved in `evidence/logs` or `reports/cron.log`
