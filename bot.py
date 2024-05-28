from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import requests
import time
import os
import telebot
import threading
import schedule
from datetime import datetime, timedelta

amount = 250000
amount_tokens = amount * 1000000000

last_burn_file = 'last_burn.json'

# Function to load the last burn transaction time from the JSON file
def load_last_burn_time():
    if os.path.exists(last_burn_file):
        with open(last_burn_file, 'r') as f:
            data = json.load(f)
            return data.get('last_burn_time')
    else:
        return None

# Function to save the last burn transaction time to the JSON file
def save_last_burn_time(last_burn_time):
    data = {'last_burn_time': last_burn_time}
    with open(last_burn_file, 'w') as f:
        json.dump(data, f)

# Function to format timedelta as "x hours, y minutes, z seconds"
def format_timedelta(td):
  hours, remainder = divmod(td.seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  return f"{hours} hours, {minutes} minutes, {seconds} seconds"


#fetching price of token

price_url = "https://api.dexscreener.com/latest/dex/search?q=0xa2eb776f262a7d001df8606f74fcfd3ee4a31cc4"
# Fetch the data
price_response = requests.get(price_url)
# Parse the JSON response
price_data = price_response.json()
# Extract the priceUsd value
price_usd = float(price_data['pairs'][0]['priceUsd'])

# Define global variables to store information about the last burn transaction
last_burn_tx_hash = None
last_burn_tx_time = None

total_bot_supply = 181000000
total_supply = 1000000000
BOT_TOKEN = '7078046885:AAGZfj4Ez28TEiygbXVAPvObCAeGh3xVPD8'  # Replace with your bot token
# Create a TeleBot instance with your bot token
bot = telebot.TeleBot(BOT_TOKEN)


# Function to send a message to the Telegram group
def send_message(message):
  bot.send_message(
      chat_id='-1002118601081',
      text=message,
      parse_mode="HTML",
      disable_web_page_preview=True)  # Replace with your group chat ID

# Function to send a message to the Telegram chat
def send_msg(chat_id, message):
  bot.send_message(
      chat_id=chat_id,
      text=message,
      parse_mode="HTML",
      disable_web_page_preview=True)


def send_video_message(video_url, message):
  bot.send_video(chat_id='-1002118601081',
                 video=video_url,
                 caption=message,
                 parse_mode="HTML")


# Constants for the RPC URL and contract details
RPC_URL = 'https://base.publicnode.com'
CONTRACT_ADDRESS = '0xa2Eb776f262A7D001Df8606F74fcFD3Ee4A31cc4'
TO_ADDRESS = '0x000000000000000000000000000000000000dEaD'  #Adjust the to addressp

# Replace with your private key
PRIVATE_KEY = '15d2c62e3a3fcc89e0a44e5025b11c1860fc376cac9fd1cfe96069f6e7eb1296'

# Create a Web3 instance connected to the specified RPC URL
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Inject PoA middleware for networks using Proof of Authority consensus
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Check for connection to the Ethereum network
try:
  # Attempt to get the latest block number
  block_number = w3.eth.block_number
  print("Connected to Ethereum network!")
except Exception as e:
  # Connection failed
  print(f"Failed to connect to Ethereum network: {e}")

# Load the contract ABI from a file
with open('abi.json') as abi_file:
  contract_abi = json.load(abi_file)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)


# Function to send a transaction
def send_transaction():
    global last_burn_tx_hash, last_burn_tx_time
    while True:
        try:
            # Check if the last burn transaction was done within the last 12 hours
            last_burn_time = load_last_burn_time()
            if last_burn_time is None or (datetime.now() - datetime.fromisoformat(last_burn_time)) >= timedelta(hours=12):
                # Define transaction details
                token_amount = Web3.toWei(amount_tokens, 'gwei')  # Adjust the amount as needed

                # Get the nonce for the transaction
                nonce = w3.eth.getTransactionCount(
                    w3.eth.account.privateKeyToAccount(PRIVATE_KEY).address)

                # Build the transaction
                transaction = contract.functions.transfer(
                    TO_ADDRESS, token_amount).buildTransaction({
                        'chainId': w3.eth.chain_id,
                        'gas': 210000,  # Adjust the gas limit as needed
                        'nonce': nonce,
                    })

                # Sign the transaction with the private key
                signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)

                # Attempt to send the transaction
                tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                print(f"Transaction sent! Hash: {tx_hash.hex()}")

                # Update last burn transaction details
                last_burn_tx_hash = tx_hash.hex()
                last_burn_tx_time = datetime.now()
                save_last_burn_time(last_burn_tx_time.isoformat())

                # Send burn transaction details to Telegram group
                message = f"""
                <b>🚨🚨<i>BURN ALERT</i>🚨🚨</b>
                <a href='https://basescan.org/tx/{tx_hash.hex()}'>❗️Burn Transaction Detected🔥</a>\n
                ℹ️ <i><u>Transaction Details:</u></i>
                - <b>Transaction Hash:</b> <code>{tx_hash.hex()}</code>
                - <b>Amount Burned:</b> <code>250,000 Tokens</code>
                - <b>Value Burned:</b> <code>${value_burned:.2f}</code>
                - <b>Time:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n
                 🐦<a href='https://x.com/thisisbased_'>Twitter</a> 💬<a href='https://t.me/ThisIsBasedFOB'>Telegram</a> 🌐<a href='https://fineonbase.wtf/'>Website</a>
                """
                send_video_message('https://i.imgur.com/NI2vjqy.mp4', message)

            else:
                # Last burn transaction occurred within the last 12 hours, wait before attempting another burn
                time_since_last_burn = datetime.now() - datetime.fromisoformat(last_burn_time)
                time_left_for_next_burn = timedelta(hours=12) - time_since_last_burn
                print(f"Last burn transaction occurred {format_timedelta(time_since_last_burn)} ago. Waiting {format_timedelta(time_left_for_next_burn)} before next burn.")
                time.sleep(time_left_for_next_burn.total_seconds())

        except Exception as e:
            print(f"Error sending transaction: {e}")
            # Send error message to Telegram group
            send_message(f"Error sending transaction: {e}")
          

# Load the last burn transaction time when the script starts
last_burn_tx_time = load_last_burn_time()

# Start the transaction sending in a separate thread
transaction_thread = threading.Thread(target=send_transaction)
transaction_thread.start()


# Define a command handler for '/stats' command
@bot.message_handler(commands=['stats'])
def send_stats(message):
  try:
    # Define the URL to get the total tokens burned
    total_burned_url = 'https://api.basescan.org/api?module=account&action=tokenbalance&contractaddress=0xa2Eb776f262A7D001Df8606F74fcFD3Ee4A31cc4&address=0x000000000000000000000000000000000000dEaD&tag=latest&apikey=I2DMDYR4A9UGZDB6VX5ZGG29PT4Y8ZSBPT'
    bot_holdings_url = 'https://api.basescan.org/api?module=account&action=tokenbalance&contractaddress=0xa2Eb776f262A7D001Df8606F74fcFD3Ee4A31cc4&address=0x9f4ab8e204646315760A9fB3995AB858e7D6CB9D&tag=latest&apikey=I2DMDYR4A9UGZDB6VX5ZGG29PT4Y8ZSBPT'

    # Send a GET request to get the total tokens burned
    response = requests.get(total_burned_url)
    holdings_response = requests.get(bot_holdings_url)
    price_url = "https://api.dexscreener.com/latest/dex/search?q=0xa2eb776f262a7d001df8606f74fcfd3ee4a31cc4"
      # Fetch the data
    price_response = requests.get(price_url)
      # Parse the JSON response
    price_data = price_response.json()
      # Extract the priceUsd value
    price_usd = float(price_data['pairs'][0]['priceUsd'])
    print(price_usd)

    # Check if the request was successful
    if response.status_code == 200:
      # Parse the JSON response
      data = response.json()
      holdings_data = holdings_response.json()
      bot_holdings = float(holdings_data.get('result')) * (10**-18)
      # Extract the result field (total tokens burned)
      total_burned = float(data.get('result')) * (10**-18)
      total_value_burned = total_burned * price_usd
      # Calculate the total percentage of the total supply burned
      percentage_burned = (total_burned / total_supply) * 100


      # Calculate the time since last burn transaction
      if last_burn_tx_time:
        time_since_last_burn = datetime.now() - last_burn_tx_time

      # Calculate the time left for the next burn transaction
      time_left_for_next_burn = timedelta(seconds=12 * 60 * 60) - (
          datetime.now() - last_burn_tx_time) % timedelta(seconds=12 * 60 * 60)
     
      stats_message = f"""
🔥 <b>Total Tokens Burned:</b> <code>{total_burned:,.0f}</code>
💥 <b>Total Percentage of Total Supply Burned:</b> <code>{percentage_burned:.6f}%</code>
💼 <b>Bot Holding:</b> <code>{bot_holdings:,.0f}</code>
💰 <b>Value Burned:</b> <code>${total_value_burned:,.2f}</code>
      """
      print(stats_message)
      # Add last burn transaction details if available
      if last_burn_tx_time:
        stats_message += f"<b></b> <a href='https://basescan.org/tx/{last_burn_tx_hash}'>🔗 Last Burn Transaction</a>\n"
        stats_message += f"<b>⏱️Time Since Last Burn:</b> <code>{format_timedelta(time_since_last_burn)}</code>\n"

      # Add time left for next burn transaction
      stats_message += f"<b>⏳Time Left for Next Burn:</b> <code>{format_timedelta(time_left_for_next_burn)}</code>\n"
      stats_message += f"""
🐦<a href='https://x.com/thisisbased_'>Twitter</a> 💬<a href='https://t.me/ThisIsBasedFOB'>Telegram</a> 🌐<a href='https://fineonbase.wtf/'>Website</a>
      """

      print("sent stats msg")
      # Send the stats message to the Telegram group
      #send_message(stats_message)

      send_video_message('https://i.imgur.com/NFrSE57.mp4', stats_message)

    else:
      print("Error:", response.text)
  except Exception as e:
    # Handle any exceptions
    print("Error:", e)
    send_message("Error occurred while fetching stats.")

# Define a command handler for '/start' command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = """
🚀🔥 Introducing the <b>OnFire Burn Bot</b> (@OnFireBurnbot)! 🔥🚀
Take your project to the next level with our powerful @OnFireBurnbot! Automate and customize your token burns with ease, while keeping your community informed and engaged. Perfect for projects on Base Chain, BSC, and ETH!
✨ Features:
 • Automated Token Burns: Set the total tokens to burn and the interval between burns.
 • Real-Time Notifications: Send instant burn notifications to your Telegram group.
 • Comprehensive Stats: Track total tokens burned with detailed stats.
 • Customizable Settings: Tailor the bot to fit your project's unique needs.
Boost your token's value and transparency effortlessly. Don't miss out – integrate our OnFire Burn bot today!
🔗 Contact @TheBasedOne 🔗
    """
    send_msg(message.chat.id, welcome_message)


# Start the bot
bot.polling()
