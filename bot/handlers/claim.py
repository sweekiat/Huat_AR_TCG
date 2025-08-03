from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db

async def claim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle claim command"""
    user = update.effective_user
    
    # Create user record if it doesn't exist
    user_exists = db.add_claim(user_id=user.id,card_code=card_code)
    


    # await update.message.reply_text(welcome_message)
