from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import time
import telebot

BOT_TOKEN = '7148574279:AAGrQmM3dJ3HhOaoQmqPB6BxqjGc5i-Ks2g'
# Create a TeleBot instance with your bot token
bot = telebot.TeleBot(BOT_TOKEN)


# Function to send a message to the Telegram group
def send_message(chat_id, message):
  bot.send_message(chat_id=chat_id, text=message)


# Define the interval between transactions in seconds
interval = 60

# Constants for the RPC URL and contract details
RPC_URL = 'https://base.publicnode.com'
CONTRACT_ADDRESS = '0xc551087B504803A204c81618a6836fA480E49c86'
TO_ADDRESS = '0x000000000000000000000000000000000000dEaD'  #Adjust the to addressp

# Replace with your private key
private_key = '985323c8e0b3ddce99e1136d368712dfea86d1326784a5fdaeb10fd63b9c4dfe'

# Check if the private key is provided
if not private_key:
  raise ValueError("Private key not provided.")

# Create a Web3 instance connected to the specified RPC URL
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Inject PoA middleware for networks using Proof of Authority consensus
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Check for connection to the Ethereum network
try:
  # Attempt to get the latest block number
  block_number = w3.eth.block_number
  print("Connected to Ethereum (Base) network!")
except Exception as e:
  # Connection failed
  print(f"Failed to connect to Ethereum (Base) network: {e}")

# Load the contract ABI from a file
with open('abi.json') as abi_file:
  contract_abi = json.load(abi_file)
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)


# Define a command handler for '/stats' command
@bot.message_handler(commands=['stats'])
def send_stats(message):
  total_amount = 0
  # Get the transactions sent to the wallet address
  transactions = w3.eth.getTransactionsByAddress(TO_ADDRESS)
  for tx in transactions:
    total_amount += tx.value
  # Convert total amount to readable format
  total_amount_eth = w3.fromWei(total_amount, 'ether')
  # Send the total amount to the user
  send_message(
      message.chat.id,
      f"Total amount sent to the wallet address: {total_amount_eth} ETH")


# Run an infinite loop to send transactions periodically
while True:
  # Define transaction details
  token_amount = Web3.toWei(1000 * 100000000,
                            'gwei')  # Adjust the amount as needed

  # Get the nonce for the transaction
  nonce = w3.eth.getTransactionCount(
      w3.eth.account.privateKeyToAccount(private_key).address)

  # Build the transaction
  transaction = contract.functions.transfer(
      TO_ADDRESS, token_amount).buildTransaction({
          'chainId': w3.eth.chain_id,
          'gas': 210000,  # Adjust the gas limit as needed
          'nonce': nonce,
      })

  # Sign the transaction with the private key
  signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

  # Attempt to send the transaction
  try:
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Transaction sent! Hash: {tx_hash.hex()}")

    # Send transaction details to Telegram group
    send_message('-4103712352', f"Transaction sent! Hash: {tx_hash.hex()}")
  except Exception as e:
    print(f"Error sending transaction: {e}")
    # Send error message to Telegram group
    send_message('-4103712352', f"Error sending transaction: {e}")

  # Wait for the specified interval before sending the next transaction
  time.sleep(interval)

# Run the bot
bot.polling()
