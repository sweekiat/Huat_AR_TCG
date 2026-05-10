from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, filters
from telethon import TelegramClient
from bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_ID, TELEGRAM_API_HASH
from bot.handlers.start import start_command
from bot.handlers.forward_messages import get_forward_handler

# Globals — no threads, no loops, just objects
ptb_app: Application = None
telethon_client: TelegramClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Everything here runs in the single asyncio event loop. No threads."""
    global ptb_app, telethon_client

    # --- startup ---
    telethon_client = TelegramClient('session_name', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await telethon_client.connect()
    if not await telethon_client.is_user_authorized():
        raise RuntimeError("Telethon client not authorized")

    ptb_app = Application.builder().token(TELEGRAM_BOT_TOKEN).updater(None).build()
    ptb_app.bot_data["telethon_client"] = telethon_client

    private_only = filters.ChatType.PRIVATE
    ptb_app.add_handler(CommandHandler("start", start_command, filters=private_only))
    ptb_app.add_handler(get_forward_handler(private_only))

    await ptb_app.initialize()
    await ptb_app.start()

    yield  # app is live here

    # --- shutdown ---
    await ptb_app.stop()
    await ptb_app.shutdown()
    await telethon_client.disconnect()


app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    await ptb_app.process_update(update)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok"}

# curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://6b1d-220-255-64-203.ngrok-free.app/webhook"