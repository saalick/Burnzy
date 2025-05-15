# burn.py

from web3 import Web3
from web3.middleware import geth_poa_middleware
import time
from datetime import datetime, timedelta
import threading
import json

from config import *
from telegram_bot import send_video_message, send_message
from utils import load_last_burn_time, save_last_burn_time, get_token_price, format_timedelta

w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

with open('abi.json') as f:
    contract_abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def burn_tokens_loop():
    while True:
        try:
            last_time = load_last_burn_time()
            if not last_time or (datetime.now() - last_time >= timedelta(hours=12)):
                amount = 250_000
                token_amt = Web3.toWei(amount * 1e9, 'wei')  # Assuming 9 decimals

                acct = w3.eth.account.privateKeyToAccount(PRIVATE_KEY)
                nonce = w3.eth.getTransactionCount(acct.address)

                tx = contract.functions.transfer(TO_ADDRESS, token_amt).buildTransaction({
                    'chainId': w3.eth.chain_id,
                    'gas': 210000,
                    'nonce': nonce,
                })

                signed_tx = acct.sign_transaction(tx)
                tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

                price = get_token_price(CONTRACT_ADDRESS)
                value = price * amount

                save_last_burn_time(datetime.now())
                msg = f"""<b>🔥 BURN EXECUTED 🔥</b>
<b>Amount:</b> <code>{amount}</code>
<b>Value:</b> <code>${value:.2f}</code>
<b>Tx:</b> <code>{tx_hash.hex()}</code>"""

                send_video_message('YOUR_VIDEO/GIF_URL', msg)
            else:
                sleep_time = timedelta(hours=12) - (datetime.now() - last_time)
                time.sleep(sleep_time.total_seconds())
        except Exception as e:
            print("Burn error:", e)
            send_message(f"Burn failed: {e}")
            time.sleep(60)

def start_burn_thread():
    threading.Thread(target=burn_tokens_loop).start()
