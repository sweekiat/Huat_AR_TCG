import random
from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
import json
from pathlib import Path
from telethon import functions

from bot.util.admin_wrapper import admin_required

channels_path = Path(__file__).parent.parent.parent / "channels.json"
with open(channels_path, 'r') as f:
    channels = json.load(f)

WAITING_FOR_MESSAGE = 1

@admin_required
async def forward_start(update, context):
    await update.message.reply_text("Please forward me a message (or reply to one).")
    return WAITING_FOR_MESSAGE

async def forward_receive(update, context):
    client = context.bot_data["telethon_client"]
    msg = update.message
    if msg.forward_origin:
        source = msg.forward_origin  # user sent a forwarded message alongside /forward
    else:
        await msg.reply_text("❌ Please forward a message.")
        return ConversationHandler.END
    for group in channels:
        try:
            await client(functions.messages.ForwardMessagesRequest(
            from_peer=source.chat.id,
            id=[source.message_id],        # must be a list
            to_peer=channels[group]["id"],
            top_msg_id=next(iter(channels[group]["topics"].values())),
            # top_msg_id=1,  # ← topic ID goes here
            random_id=[random.randint(0, 2**63)]  # required — telethon won't auto-generate this
                ))
        except Exception as e:
            await msg.reply_text(f"❌ Error forwarding message: {e} (for group {group})")
            continue
        
    await msg.reply_text("✅ Message forwarded successfully!")
    return ConversationHandler.END

async def forward_cancel(update, context):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END



def get_forward_handler(private_only):
    return ConversationHandler(
        entry_points=[CommandHandler("forward", forward_start, filters=private_only)],
        states={
            WAITING_FOR_MESSAGE: [
                MessageHandler(filters.ALL & private_only, forward_receive)
            ],
        },
        fallbacks=[CommandHandler("cancel", forward_cancel)],
    )
