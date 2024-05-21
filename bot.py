from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import requests
import time
import telebot
import threading
import schedule
from datetime import datetime, timedelta


# Function to format timedelta as "x hours, y minutes, z seconds"
def format_timedelta(td):
  hours, remainder = divmod(td.seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  return f"{hours} hours, {minutes} minutes, {seconds} seconds"


# Define global variables to store information about the last burn transaction
last_burn_tx_hash = None
last_burn_tx_time = None

total_bot_supply = 36000000000
total_supply = 100000000000
BOT_TOKEN = '7078046885:AAGBbyfvFRjAMkljA0tRbkKtrRTjcvsurAc'  # Replace with your bot token
# Create a TeleBot instance with your bot token
bot = telebot.TeleBot(BOT_TOKEN)


# Function to send a message to the Telegram group
def send_message(message):
  bot.send_message(
      chat_id='-4103712352',
      text=message,
      parse_mode="HTML",
      disable_web_page_preview=True)  # Replace with your group chat ID


# Constants for the RPC URL and contract details
RPC_URL = 'https://base.publicnode.com'
CONTRACT_ADDRESS = '0xDdaCA8806fbbFC0fd5dCd92E3d30714C542c96f8'
TO_ADDRESS = '0x000000000000000000000000000000000000dEaD'  #Adjust the to addressp

# Replace with your private key
PRIVATE_KEY = 'edda48e802e7535aeac89e8cff36adacd6831610e45a5864cf79cd9b1a4dd0c5'

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
      # Define transaction details
      token_amount = Web3.toWei(1000,
                                'gwei')  # Adjust the amount as needed

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

      # Send transaction details to Telegram group
      # send_message(f"Transaction sent! Hash: {tx_hash.hex()}")
      message = f"""
<b>🚨🚨<i>BURN ALERT</i>🚨🚨</b>
<a href='https://basescan.org/tx/{tx_hash.hex()}'>❗️Burn Transaction Detected🔥</a>\n
ℹ️ <i><u>Transaction Details:</u></i>
- <b>Transaction Hash:</b> <code>{tx_hash.hex()}</code>
- <b>Amount Burned:</b> <code>250,000 Tokens</code>
- <b>Value Burned:</b> $ <code>N/A</code>
- <b>Time:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n
 🐦<a href='https://twitter.com/your_twitter'>Twitter</a> 💬<a href='https://t.me/your_telegram'>Telegram</a> 🔍<a href='https://etherscan.io/'>Contract</a>
      """
      # Send the message to the Telegram group with HTML formatting
      send_message(message)
    except Exception as e:
      print(f"Error sending transaction: {e}")
      # Send error message to Telegram group
      send_message(f"Error sending transaction: {e}")

    # Wait for 12 hours before sending the next transaction
    time.sleep(12 * 60 * 60)


# Start the transaction sending in a separate thread
transaction_thread = threading.Thread(target=send_transaction)
transaction_thread.start()


# Define a command handler for '/stats' command
@bot.message_handler(commands=['stats'])
def send_stats(message):
  try:
    # Define the URL to get the total tokens burned
    total_burned_url = 'https://api.basescan.org/api?module=account&action=tokenbalance&contractaddress=0xDdaCA8806fbbFC0fd5dCd92E3d30714C542c96f8&address=0x000000000000000000000000000000000000dEaD&tag=latest&apikey=I2DMDYR4A9UGZDB6VX5ZGG29PT4Y8ZSBPT'

    # Send a GET request to get the total tokens burned
    response = requests.get(total_burned_url)

    # Check if the request was successful
    if response.status_code == 200:
      # Parse the JSON response
      data = response.json()

      # Extract the result field (total tokens burned)
      total_burned = float(data.get('result')) * (10**-9)

      # Calculate the total percentage of the total supply burned
      percentage_burned = (total_burned / total_supply) * 100

      # Calculate the bot holding
      bot_holding = total_bot_supply - total_burned

      # Calculate the time since last burn transaction
      if last_burn_tx_time:
        time_since_last_burn = datetime.now() - last_burn_tx_time

      # Calculate the time left for the next burn transaction
      time_left_for_next_burn = timedelta(seconds=12 * 60 * 60) - (
          datetime.now() - last_burn_tx_time) % timedelta(seconds=12 * 60 * 60)

      stats_message = f"""
🔥 <b>Total Tokens Burned:</b> <code>{total_burned:.0f}</code>
💥 <b>Total Percentage of Total Supply Burned:</b> <code>{percentage_burned:.6f}%</code>
💼 <b>Bot Holding:</b> <code>{bot_holding:.0f}</code>
💰 <b>Value Burned:</b> $ <code>N/A</code>
      """
      # Add last burn transaction details if available
      if last_burn_tx_time:
        stats_message += f"<b></b> <a href='https://basescan.org/tx/{last_burn_tx_hash}'>🔗 Last Burn Transaction</a>\n"
        stats_message += f"<b>⏱️Time Since Last Burn:</b> <code>{format_timedelta(time_since_last_burn)}</code>\n"

      # Add time left for next burn transaction
      stats_message += f"<b>⏳Time Left for Next Burn:</b> <code>{format_timedelta(time_left_for_next_burn)}</code>\n"
      stats_message += f"""
🐦<a href='https://twitter.com/your_twitter'>Twitter</a> 💬<a href='https://t.me/your_telegram'>Telegram</a> 🔍<a href='https://etherscan.io/'>Contract</a>
      """

      # Send the stats message to the Telegram group
      #send_message(stats_message)
      bot.send_animation(chat_id='-4103712352',
                         animation='https://i.imgur.com/eiA66wE.gif',
                         caption=stats_message,
                         parse_mode='HTML')

    else:
      print("Error:", response.text)
  except Exception as e:
    # Handle any exceptions
    print("Error:", e)
    send_message("Error occurred while fetching stats.")


# Start the bot
bot.polling()
