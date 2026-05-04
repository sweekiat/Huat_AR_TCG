from telegram import Update
from telegram.ext import ContextTypes
from bot.util.admin_wrapper import admin_required
from telethon import TelegramClient, events, sync

@admin_required
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE, client: TelegramClient):
    """Handle /forward_message command"""
    # Get message data from command arguments
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /forward_message <telegram_message_id>")
        return
    telegram_message_id = context.args[0]

    # Use the Telethon client to forward the message (incomplete )
    # supposed to get the message and forward it to the target chat
    
    try:
        await client.forward_messages('kyliesk123', telegram_message_id)
        await update.message.reply_text("Message forwarded successfully!")
    except Exception as e:
        await update.message.reply_text(f"Error forwarding message: {e}")
    