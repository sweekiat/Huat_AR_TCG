from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command"""
    user_id = update.effective_user.id
    
    # Get user's claimed items from database
    items = db.get_user_items(user_id)
    
    if not items:
        await update.message.reply_text("You haven't claimed any items yet!")
        return
    
    # Format the items list
    items_text = "Your claimed items:\n\n"
    for i, item in enumerate(items, 1):
        # Adjust these fields based on your database schema
        item_name = item.get('name', 'Unknown Item')
        claim_date = item.get('created_at', 'Unknown Date')
        items_text += f"{i}. {item_name} (claimed: {claim_date})\n"
    
    await update.message.reply_text(items_text)