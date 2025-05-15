# utils.py

from datetime import datetime
import json
import os
import requests

LAST_BURN_FILE = 'last_burn.json'

def load_last_burn_time():
    if os.path.exists(LAST_BURN_FILE):
        with open(LAST_BURN_FILE, 'r') as f:
            data = json.load(f)
            time_str = data.get('last_burn_time')
            return datetime.fromisoformat(time_str) if time_str else None
    return None

def save_last_burn_time(dt):
    with open(LAST_BURN_FILE, 'w') as f:
        json.dump({'last_burn_time': dt.isoformat()}, f)

def format_timedelta(td):
    h, r = divmod(td.total_seconds(), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}h {int(m)}m {int(s)}s"

def get_token_price(token_address):
    url = f"https://api.dexscreener.com/latest/dex/search?q={token_address}"
    res = requests.get(url)
    return float(res.json()['pairs'][0]['priceUsd'])
