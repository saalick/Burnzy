# stats.py

import requests
from datetime import datetime, timedelta
from config import *
from utils import get_token_price, load_last_burn_time, format_timedelta
from telegram_bot import send_video_message, send_private_msg

def handle_stats_command(chat_id):
    try:
        burned = requests.get(
            f'https://api.basescan.org/api?module=account&action=tokenbalance&contractaddress={CONTRACT_ADDRESS}&address={DEAD_ADDRESS}&tag=latest&apikey={BURN_API_KEY}'
        ).json()['result']

        holdings = requests.get(
            f'https://api.basescan.org/api?module=account&action=tokenbalance&contractaddress={CONTRACT_ADDRESS}&address={BOT_ADDRESS}&tag=latest&apikey={BURN_API_KEY}'
        ).json()['result']

        burned = float(burned) * 1e-18
        holdings = float(holdings) * 1e-18
        price = get_token_price(CONTRACT_ADDRESS)

        value_burned = burned * price
        percent = (burned / TOTAL_SUPPLY) * 100

        last_burn = load_last_burn_time()
        time_since = datetime.now() - last_burn
        time_left = timedelta(hours=12) - time_since

        msg = f"""
🔥 <b>Total Burned:</b> <code>{burned:,.0f}</code>
💥 <b>Percentage:</b> <code>{percent:.6f}%</code>
💼 <b>Bot Holdings:</b> <code>{holdings:,.0f}</code>
💰 <b>Value Burned:</b> <code>${value_burned:,.2f}</code>
🕒 <b>Last Burn:</b> <code>{format_timedelta(time_since)} ago</code>
⏳ <b>Next Burn In:</b> <code>{format_timedelta(time_left)}</code>
"""
        send_video_message('YOUR_VIDEO/GIF URL', msg)
    except Exception as e:
        print("Stats error:", e)
        send_private_msg(chat_id, "Failed to fetch stats.")
