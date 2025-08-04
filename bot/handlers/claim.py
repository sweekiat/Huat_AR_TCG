from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db

async def claim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle claim message (not command)"""
    user = update.effective_user
    
    # Debug prints
    print(f"Message exists: {update.message is not None}")
    print(f"Reply to message exists: {update.message.reply_to_message is not None}")
    
    # Get the message being replied to
    if update.message.reply_to_message:
        original_message = update.message.reply_to_message
        card_code = original_message.text
        
        # Additional debug info
        print(f"Original message text: '{card_code}'")
        
        await update.message.reply_text(f"✅ Detected reply to message: {card_code}")
    else:
        await update.message.reply_text("Please reply to a message to claim a card.")
        return
    
    print(f"User ID: {user.id}, Card Code: {card_code}")
