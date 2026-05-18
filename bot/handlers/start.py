from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    # Create user record if it doesn't exist
    
    welcome_message = f"""Hello {user.username}! Welcome to Huat_AR_tcg.

Here are the commands I can respond to:
/find - to find and add group ids
/forward - forwards a message to a group
/list - see existing list of group and ids
""" 

    await update.message.reply_text(welcome_message)
