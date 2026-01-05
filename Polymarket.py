import os
import requests
import pandas as pd
from datetime import datetime, timezone

# Polymarket Gamma Markets API overview (read-only markets data)
# Docs: https://docs.polymarket.com/... (see citations in chat)
BASE = "https://gamma-api.polymarket.com"

def fetch_markets(limit=50, active=True):
    params = {
        "limit": limit,
        "active": str(active).lower(),
    }
    r = requests.get(f"{BASE}/markets", params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def build_df(data):
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for m in data:
        rows.append({
            "snapshot_time": now,
            "market_id": m.get("id"),
            "question": m.get("question"),
            "slug": m.get("slug"),
            "end_date": m.get("endDate"),
            "outcomes": m.get("outcomes"),
            "outcome_prices": m.get("outcomePrices"),
            "volume": m.get("volume"),
            "liquidity": m.get("liquidity"),
        })
    return pd.DataFrame(rows)

def save_csv(df, out_dir="reports", prefix="all_active_markets"):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(out_dir, f"{prefix}_{ts}.csv")
    df.to_csv(path, index=False)
    return path

def main():
    data = fetch_markets(limit=50, active=True)
    df = build_df(data)
    out_path = save_csv(df)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()