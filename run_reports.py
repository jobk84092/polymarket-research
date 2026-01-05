import argparse
import importlib.util
import os
import json
from datetime import datetime, timezone

# We directly import the modules by filename to avoid path issues with spaces
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_module(module_path):
    spec = importlib.util.spec_from_file_location(os.path.basename(module_path), module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description="Run Polymarket reports and save CSVs.")
    parser.add_argument("--top50", action="store_true", help="Run only the Top 50 by 24h volume report")
    parser.add_argument("--all-active", action="store_true", help="Run only the All Active Markets snapshot")
    parser.add_argument("--outdir", default=None, help="Output folder (overrides config)")
    parser.add_argument("--limit", type=int, default=None, help="Limit for markets (overrides config)")
    args = parser.parse_args()

    # Load config and apply CLI overrides
    cfg_path = os.path.join(BASE_DIR, "config.json")
    cfg = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
    outdir = os.path.join(BASE_DIR, args.outdir or cfg.get("outdir", "reports"))
    limit = int(args.limit or cfg.get("limit", 50))
    os.makedirs(outdir, exist_ok=True)

    top50_path = os.path.join(BASE_DIR, "top 50 polymarket.py")
    all_active_path = os.path.join(BASE_DIR, "Polymarket.py")

    run_top = args.top50 or (not args.top50 and not args.all_active)
    run_all = args.all_active or (not args.top50 and not args.all_active)

    if run_top:
        mod_top = load_module(top50_path)
        try:
            data = mod_top.top_markets_by_24h(limit=limit)
            df = mod_top.build_df(data)
            path = mod_top.save_csv(df, out_dir=outdir, prefix="top_markets_24h")
            print(f"Saved: {path}")
        except Exception as e:
            print(f"Error running top_markets_24h: {e}")

    if run_all:
        mod_all = load_module(all_active_path)
        try:
            data = mod_all.fetch_markets(limit=limit, active=True)
            df = mod_all.build_df(data)
            path = mod_all.save_csv(df, out_dir=outdir, prefix="all_active_markets")
            print(f"Saved: {path}")
        except Exception as e:
            print(f"Error running all_active_markets: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
