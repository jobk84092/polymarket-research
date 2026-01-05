import os
import requests
import pandas as pd
from datetime import datetime, timezone

BASE = "https://gamma-api.polymarket.com"

def top_markets_by_24h(limit=50, offset=0, active=True):
    params = {
        "limit": limit,
        "offset": offset,
        "active": str(active).lower(),
        "order": "volume24hr",
        "ascending": "false",
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
            "question": m.get("question"),
            "slug": m.get("slug"),
            "category": m.get("category"),
            "endDate": m.get("endDate"),
            "volume24hr": m.get("volume24hr"),
            "volume_total": m.get("volumeNum"),
            "liquidity": m.get("liquidityNum"),
            "outcomes": m.get("outcomes"),
            "outcomePrices": m.get("outcomePrices"),
        })
    return pd.DataFrame(rows)

def save_csv(df, out_dir="reports", prefix="top_markets_24h"):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(out_dir, f"{prefix}_{ts}.csv")
    df.to_csv(path, index=False)
    return path

def main():
    data = top_markets_by_24h(limit=50)
    df = build_df(data)
    # Save the full dataset, not just 15 rows
    out_path = save_csv(df)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()