# telegram_bot.py

import telebot
from config import BOT_TOKEN, GROUP_CHAT_ID

bot = telebot.TeleBot(BOT_TOKEN)

def send_message(msg):
    bot.send_message(chat_id=GROUP_CHAT_ID, text=msg, parse_mode="HTML", disable_web_page_preview=True)

def send_video_message(video_url, caption):
    bot.send_video(chat_id=GROUP_CHAT_ID, video=video_url, caption=caption, parse_mode="HTML")

def send_private_msg(chat_id, msg):
    bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML", disable_web_page_preview=True)
