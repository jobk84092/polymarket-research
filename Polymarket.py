import os
import json
import requests
import pandas as pd
from datetime import datetime, timezone
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Polymarket Gamma Markets API overview (read-only markets data)
# Docs: https://docs.polymarket.com/... (see citations in chat)
BASE = "https://gamma-api.polymarket.com"

def fetch_markets(limit=50, active=True):
    session = get_session()
    params = {
        "limit": int(limit),
        "active": str(active).lower(),
    }
    r = session.get(f"{BASE}/markets", params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def get_session(retries: int = 3, backoff: float = 0.5):
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def build_df(data):
    now = datetime.now(timezone.utc).isoformat()
    rows = []
    for m in data:
        # Normalize types and keys; some fields may be missing
        end = m.get("endDate")
        category = m.get("category")
        volume_total = _to_float(m.get("volumeNum") or m.get("volume"))
        liquidity = _to_float(m.get("liquidityNum") or m.get("liquidity"))
        volume24hr = _to_float(m.get("volume24hr"))

        rows.append({
            "snapshot_time": now,
            "market_id": m.get("id"),
            "question": m.get("question"),
            "slug": m.get("slug"),
            "category": category,
            "endDate": end,
            "volume24hr": volume24hr,
            "volume_total": volume_total,
            "liquidity": liquidity,
            "outcomes": m.get("outcomes"),
            "outcomePrices": m.get("outcomePrices"),
        })
    df = pd.DataFrame(rows)
    return df

def _to_float(x: Optional[object]) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None

def save_csv(df, out_dir="reports", prefix="all_active_markets", gzip=False, partition_by_date=True, latest=True, rolling=True):
    # Partition by UTC date folder
    base_out = out_dir
    if partition_by_date:
        date_dir = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        base_out = os.path.join(out_dir, date_dir)
    os.makedirs(base_out, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ext = ".csv.gz" if gzip else ".csv"
    filename = f"{prefix}_{ts}{ext}"
    path = os.path.join(base_out, filename)
    df.to_csv(path, index=False, compression=("gzip" if gzip else None))

    # Maintain latest copy
    if latest:
        latest_path = os.path.join(out_dir, f"latest_{prefix}{ext}")
        df.to_csv(latest_path, index=False, compression=("gzip" if gzip else None))

    # Append to rolling CSV
    if rolling:
        roll_dir = os.path.join(out_dir, "rolling")
        os.makedirs(roll_dir, exist_ok=True)
        roll_path = os.path.join(roll_dir, f"{prefix}_rolling{ext}")
        # Append with header if file does not exist
        df.to_csv(roll_path, index=False, compression=("gzip" if gzip else None), mode="a", header=not os.path.exists(roll_path))

    return path

def load_config(path="config.json"):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def main():
    cfg = load_config()
    limit = cfg.get("limit", 50)
    out_dir = cfg.get("outdir", "reports")
    try:
        data = fetch_markets(limit=limit, active=True)
        df = build_df(data)
        out_path = save_csv(df, out_dir=out_dir, prefix="all_active_markets")
        print(f"Saved: {out_path}")
    except Exception as e:
        print(f"Error generating all_active_markets: {e}")

if __name__ == "__main__":
    main()