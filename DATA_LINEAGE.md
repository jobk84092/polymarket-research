# Data Lineage

Tracks where data originates, how it is transformed, and where outputs are consumed.

## Source Systems

| System | URL | Auth | Type |
|---|---|---|---|
| Polymarket Gamma API | `https://gamma-api.polymarket.com` | None (public, read-only) | REST/JSON |

### Key endpoint: `/markets`

```
GET https://gamma-api.polymarket.com/markets
  ?limit=50
  &active=true
  [&order=volume24hr&ascending=false]   ← top-50 variant
```

Fields consumed from each market object:

| Raw field | Mapped column | Notes |
|---|---|---|
| `id` | `market_id` | Integer market identifier |
| `question` | `question` | Human-readable market question |
| `slug` | `slug` | URL slug |
| `category` | `category` | May be `null` for some markets |
| `endDate` | `endDate` | ISO 8601 resolution date |
| `volumeNum` / `volume` | `volume_total` | Lifetime volume (USD); prefers `volumeNum` |
| `liquidityNum` / `liquidity` | `liquidity` | Current liquidity (USD) |
| `volume24hr` | `volume24hr` | Rolling 24-hour volume (USD) |
| `outcomes` | `outcomes` | JSON array of outcome labels |
| `outcomePrices` | `outcomePrices` | JSON array of current prices (0–1) |

## Ingestion

- Script: `Polymarket.py` (`fetch_markets` → `build_df`) for all-active snapshots.
- Script: `top 50 polymarket.py` for top-50 by 24h volume.
- Orchestrator: `run_reports.py` — calls both scripts, accepts `--limit`, `--outdir`.
- A `snapshot_time` column (UTC ISO 8601) is added at ingestion time.

## Transformations

1. `_to_float()` normalises volume/liquidity values (handles `None`, strings, numeric).
2. No other transformations are applied — raw API values are stored as-is to preserve fidelity.

## Outputs

| Output path | Description | Updated |
|---|---|---|
| `reports/YYYY-MM-DD/all_active_markets_<ts>.csv.gz` | Partitioned daily snapshot (all active) | Each run |
| `reports/YYYY-MM-DD/top_markets_24h_<ts>.csv.gz` | Partitioned daily snapshot (top 50) | Each run |
| `reports/latest_all_active_markets.csv.gz` | Latest all-active snapshot | Overwritten each run |
| `reports/latest_top_markets_24h.csv.gz` | Latest top-50 snapshot | Overwritten each run |
| `reports/rolling/all_active_markets_rolling.csv.gz` | Appended time-series (all active) | Appended each run |
| `reports/rolling/top_markets_24h_rolling.csv.gz` | Appended time-series (top 50) | Appended each run |

## Consumers

- `review_latest.py` — terminal review of latest snapshots.
- `notebooks/analysis.ipynb` — charts and trend summaries.
- `polymarket_alerts.py` — reads live API prices directly (does not consume CSVs).
- Any SQL or BI tool pointed at the CSV/GZ files in `reports/`.

## Notes

- The Gamma API is public and unauthenticated. Rate limits are not published; the client uses exponential back-off on 429/5xx responses.
- `outcomes` and `outcomePrices` are stored as JSON strings. To analyse at the outcome level, parse them with `json.loads()` and explode into long format.
- Rolling files are append-only; duplicate rows may appear if a run is retried on the same day.
