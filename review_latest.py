"""
review_latest.py – display the latest Polymarket snapshot CSV in the terminal.

Usage:
    python review_latest.py                   # top-50 report, 20 rows
    python review_latest.py --report all      # all-active report
    python review_latest.py --report both     # both reports
    python review_latest.py --rows 50         # show 50 rows
    python review_latest.py --fetch           # pull fresh data first, then review
    python review_latest.py --export          # also write a plain CSV for spreadsheet review
"""
import argparse
import os
import subprocess
import sys

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

FILES = {
    "top": os.path.join(REPORTS_DIR, "latest_top_markets_24h.csv.gz"),
    "all": os.path.join(REPORTS_DIR, "latest_all_active_markets.csv.gz"),
}

DISPLAY_COLS = ["question", "category", "volume24hr", "volume_total", "liquidity", "endDate"]


def fetch_fresh() -> None:
    """Re-run run_reports.py to pull the latest data from the Gamma API."""
    script = os.path.join(BASE_DIR, "run_reports.py")
    print("Fetching fresh data from Polymarket API...")
    result = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        print(f"Warning: run_reports.py exited with code {result.returncode}")
        if result.stderr:
            print(result.stderr.strip())


def load(report: str) -> pd.DataFrame:
    path = FILES[report]
    if not os.path.exists(path):
        sys.exit(
            f"Error: {path} not found.\n"
            "Run `python run_reports.py` first to generate the data, "
            "or use `--fetch` to do it automatically."
        )
    df = pd.read_csv(path)
    if "snapshot_time" in df.columns:
        df["snapshot_time"] = pd.to_datetime(df["snapshot_time"], errors="coerce")
    if "endDate" in df.columns:
        df["endDate"] = pd.to_datetime(df["endDate"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def summarize(df: pd.DataFrame, label: str) -> None:
    snap = df["snapshot_time"].dropna().max() if "snapshot_time" in df.columns else "N/A"
    total_vol24 = df["volume24hr"].sum() if "volume24hr" in df.columns else 0
    total_liq = df["liquidity"].sum() if "liquidity" in df.columns else 0
    print(f"\n{'=' * 70}")
    print(f"  {label}")
    print(f"{'=' * 70}")
    print(f"  Snapshot time : {snap}")
    print(f"  Markets shown : {len(df)}")
    print(f"  Total 24h vol : ${total_vol24:,.0f}")
    print(f"  Total liquidity: ${total_liq:,.0f}")
    print(f"{'=' * 70}\n")


def display(df: pd.DataFrame, rows: int) -> None:
    cols = [c for c in DISPLAY_COLS if c in df.columns]
    view = df.sort_values("volume24hr", ascending=False).head(rows)[cols].copy()
    for col in ("volume24hr", "volume_total", "liquidity"):
        if col in view.columns:
            view[col] = view[col].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "-")
    if "category" in view.columns:
        view["category"] = view["category"].fillna("-")
    pd.set_option("display.max_colwidth", 60)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", rows + 5)
    print(view.to_string(index=True))
    print()


def export_csv(df: pd.DataFrame, label: str) -> None:
    out_path = os.path.join(REPORTS_DIR, f"review_{label}.csv")
    df.drop(columns=["snapshot_time"], errors="ignore").to_csv(out_path, index=False)
    print(f"Exported plain CSV → {out_path}")


def main() -> None:
    p = argparse.ArgumentParser(description="Review the latest Polymarket CSV snapshot.")
    p.add_argument(
        "--report",
        choices=["top", "all", "both"],
        default="top",
        help="Which snapshot to review: top (24h volume), all (active), or both (default: top)",
    )
    p.add_argument(
        "--rows",
        type=int,
        default=20,
        help="Number of rows to display (default: 20)",
    )
    p.add_argument(
        "--fetch",
        action="store_true",
        help="Re-run run_reports.py first to pull fresh data from the API",
    )
    p.add_argument(
        "--export",
        action="store_true",
        help="Write a plain (uncompressed) CSV to reports/ for spreadsheet review",
    )
    args = p.parse_args()

    if args.fetch:
        fetch_fresh()

    reports_to_run = ["top", "all"] if args.report == "both" else [args.report]
    labels = {"top": "Top Markets by 24h Volume", "all": "All Active Markets"}

    for report in reports_to_run:
        df = load(report)
        summarize(df, labels[report])
        display(df, args.rows)
        if args.export:
            export_csv(df, report)


if __name__ == "__main__":
    main()
