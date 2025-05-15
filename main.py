# main.py

from telegram_bot import bot
from burn import start_burn_thread
from stats import handle_stats_command

@bot.message_handler(commands=['stats'])
def on_stats(message):
    handle_stats_command(message.chat.id)

if __name__ == '__main__':
    start_burn_thread()
    bot.polling()
