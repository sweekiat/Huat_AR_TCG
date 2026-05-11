from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from telethon import functions
from bot.util.admin_wrapper import admin_required

WAITING_FOR_MESSAGE = 1
@admin_required
async def find_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please Choose a group.")
    return WAITING_FOR_MESSAGE

async def forward_receive(update, context):
    client = context.bot_data["telethon_client"]
    msg = update.message
    if msg.forward_origin:
        source = msg.forward_origin  # user sent a forwarded message alongside /forward
    else:
        await msg.reply_text("❌ Please forward a message.")
        return ConversationHandler.END
    try:
        await client
        await msg.reply_text("✅ Message forwarded successfully!")
    except Exception as e:
        await msg.reply_text(f"❌ Error forwarding message: {e}")
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

    
    