# generate_session.py
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from bot.config import TELEGRAM_API_ID, TELEGRAM_API_HASH

with TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
    print(client.session.save())