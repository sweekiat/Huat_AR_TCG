import json
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from bot.util.admin_wrapper import admin_required
from telethon import TelegramClient

# Load channels configuration
channels_path = Path(__file__).parent.parent.parent / "channels.json"
with open(channels_path, 'r') as f:
    channels = json.load(f)



@admin_required
async def forward_message(update: Update, client: TelegramClient):
    """Handle /forward_message command — user sends /forward WITH a forwarded message"""
    msg = update.message

    # Check if the message itself is a forward OR has a replied forwarded message
    source = None
    if msg.forward_origin:
        source = msg  # user sent a forwarded message alongside /forward
    elif msg.reply_to_message:
        source = msg.reply_to_message  # user replied to a message
    else:
        await msg.reply_text(
            "Please either:\n"
            "• Forward a message to me with /forward\n"
            "• Reply to a message with /forward",
            parse_mode="Markdown"
        )
        return

    try:
        await client.forward_messages(
            entity='kyliesk123',
            messages=source.message_id,
            from_peer=source.chat_id,
            top_msg_id=channels["BakaDegenTCG"]["topics"]["Marketplace"]
        )
        await msg.reply_text("✅ Message forwarded successfully!")
    except Exception as e:
        await msg.reply_text(f"❌ Error forwarding message: {e}")
    