import os, time, json, random, argparse
from datetime import datetime, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

GAMMA = "https://gamma-api.polymarket.com"
STATE_FILE = "pm_state.json"

def get_session(retries: int = 3, backoff: float = 0.5):
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET", "POST"))
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s

def tg_send(text: str, token: str, chat_id: str, notify: bool) -> None:
    if not notify:
        return
    if not (token and chat_id):
        print("⚠️ Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID env vars.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=20)
    except Exception as e:
        print("Telegram send failed:", e)

def fetch_top_markets(session, limit=50):
    params = {
        "limit": int(limit),
        "active": "true",
        "order": "volume24hr",
        "ascending": "false",
    }
    r = session.get(f"{GAMMA}/markets", params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def parse_yes_price(market: dict):
    outcomes = market.get("outcomes") or []
    prices = market.get("outcomePrices") or []
    if not outcomes or not prices or len(outcomes) != len(prices):
        return None
    mapping = {str(o).strip().lower(): float(p) for o, p in zip(outcomes, prices)}
    return mapping.get("yes", float(prices[0]))

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)

def run(poll_seconds=60, top_n=50, jump_points=0.08, notify=True, cooldown_seconds=300, once=False):
    """
    poll_seconds: how often to check
    jump_points: 0.08 = 8 percentage points (since prices are 0..1)
    notify: whether to send Telegram notifications
    cooldown_seconds: minimum seconds between alerts per market
    """
    # Load env from .env if available
    if load_dotenv:
        load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    session = get_session()
    state = load_state()
    last_alert = {}  # slug -> timestamp
    tg_send("✅ Polymarket tracker started.", token, chat_id, notify)

    while True:
        cycle_start = time.time()
        now = datetime.now(timezone.utc).isoformat()
        try:
            markets = fetch_top_markets(session, limit=top_n)
        except Exception as e:
            print("Fetch error:", e)
            sleep_for = poll_seconds + random.uniform(0, 2)
            time.sleep(sleep_for)
            continue

        alerts = 0
        processed = 0
        for m in markets:
            slug = m.get("slug") or str(m.get("id"))
            q = (m.get("question") or "").strip()
            yes = parse_yes_price(m)
            if yes is None:
                continue
            processed += 1

            prev = state.get(slug)
            state[slug] = {"t": now, "yes": yes, "q": q}

            if prev:
                delta = yes - float(prev["yes"])
                if abs(delta) >= jump_points:
                    # cooldown check
                    last = last_alert.get(slug, 0)
                    if time.time() - last < cooldown_seconds:
                        continue
                    msg = (
                        f"⚡ Move detected\n"
                        f"{q}\n"
                        f"YES: {prev['yes']:.3f} → {yes:.3f} (Δ {delta:+.3f})\n"
                        f"Slug: {slug}\n"
                        f"Time: {now}"
                    )
                    print(msg)
                    tg_send(msg, token, chat_id, notify)
                    last_alert[slug] = time.time()
                    alerts += 1

        save_state(state)
        elapsed = time.time() - cycle_start
        print(f"Heartbeat: processed={processed}, alerts={alerts}, elapsed={elapsed:.2f}s")
        if once:
            break
        sleep_for = poll_seconds + random.uniform(0, 2)
        time.sleep(sleep_for)

def parse_args():
    p = argparse.ArgumentParser(description="Polymarket alerts for YES price moves")
    p.add_argument("--poll-seconds", type=int, default=60, help="Polling interval seconds")
    p.add_argument("--top-n", type=int, default=50, help="Number of markets to check")
    p.add_argument("--jump-points", type=float, default=0.08, help="Minimum absolute change in YES price (0..1)")
    p.add_argument("--notify", action="store_true", help="Enable Telegram notifications")
    p.add_argument("--cooldown-seconds", type=int, default=300, help="Cooldown per market between alerts")
    p.add_argument("--once", action="store_true", help="Run a single cycle (useful for CI)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run(
        poll_seconds=args.poll_seconds,
        top_n=args.top_n,
        jump_points=args.jump_points,
        notify=args.notify,
        cooldown_seconds=args.cooldown_seconds,
        once=args.once,
    )