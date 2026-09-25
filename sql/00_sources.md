# SQL Sources

Document source systems, table locations, access notes, and source-of-truth assumptions for SQL work.

## Source: Polymarket Gamma API

- **URL:** `https://gamma-api.polymarket.com/markets`
- **Auth:** None (public, read-only REST API)
- **Granularity:** One row per prediction market
- **Refresh cadence:** Pulled on-demand via `run_reports.py`; scheduled via GitHub Actions weekly or daily cron

## Source-of-Truth Assumptions

- `market_id` (`id` in the API) is the stable primary key for a market.
- `snapshot_time` records when the row was ingested (UTC). It is **not** the market creation time.
- `volume_total` and `liquidity` are point-in-time values as of the snapshot — they will change between snapshots.
- `outcomePrices` are implied probabilities (range 0–1); multiply by 100 for percentage display.

## Local "Tables" (CSV files treated as tables)

| "Table" | File | Primary key | Notes |
|---|---|---|---|
| `top_markets_snapshot` | `reports/latest_top_markets_24h.csv.gz` | `market_id` + `snapshot_time` | Top 50 by 24h volume at last run |
| `all_markets_snapshot` | `reports/latest_all_active_markets.csv.gz` | `market_id` + `snapshot_time` | All active markets at last run |
| `top_markets_history` | `reports/rolling/top_markets_24h_rolling.csv.gz` | `market_id` + `snapshot_time` | Append-only time series |
| `all_markets_history` | `reports/rolling/all_active_markets_rolling.csv.gz` | `market_id` + `snapshot_time` | Append-only time series |

## Common Query Patterns

```sql
-- Latest snapshot: top markets sorted by 24h volume
SELECT question, volume24hr, volume_total, liquidity, endDate
FROM top_markets_snapshot
ORDER BY volume24hr DESC
LIMIT 20;

-- Rolling trend: daily total 24h volume across top markets
SELECT DATE(snapshot_time) AS date, SUM(volume24hr) AS daily_vol
FROM top_markets_history
GROUP BY DATE(snapshot_time)
ORDER BY date;

-- Markets with highest liquidity in latest all-active snapshot
SELECT question, liquidity, volume_total
FROM all_markets_snapshot
WHERE liquidity IS NOT NULL
ORDER BY liquidity DESC
LIMIT 20;
```

## Access Notes

- Files are not in a database — query them with `pandas.read_csv()`, DuckDB, or any CSV-aware SQL engine.
- DuckDB example:

```python
import duckdb
conn = duckdb.connect()
df = conn.execute(
    "SELECT * FROM read_csv_auto('reports/latest_top_markets_24h.csv.gz') ORDER BY volume24hr DESC LIMIT 10"
).df()
```

## Known Limitations

- `category` is often `NULL`; do not rely on it for grouping without handling nulls.
- Rolling files may contain duplicate rows if a run was retried on the same day.
- `outcomes` and `outcomePrices` are stored as JSON strings — cast/parse before using in SQL aggregations.

