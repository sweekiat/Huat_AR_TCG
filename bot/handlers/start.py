from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Create user record if it doesn't exist
    user_exists = db.user_exists(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    welcome_message = f"""Hello {user.username}! Welcome to Huat_AR_tcg.

Here are the commands I can respond to:
/list - Lists all of your claimed items
/invoice - Generates your invoice""" if user_exists else f"It seems like you have not claimed any items {user.username} {user.id}. Do check us out at @Huat_AR_TCG."

    await update.message.reply_text(welcome_message)
