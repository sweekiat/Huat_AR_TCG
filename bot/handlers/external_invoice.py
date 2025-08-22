from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db
from bot.util.admin_wrapper import admin_required

@admin_required
async def external_invoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /external-invoice command"""
    user_id = update.effective_user.id
    print(f"External invoice command triggered by user: {user_id} {update.effective_user.username}")
    # Get invoice data from database
    # invoice_data = db.create_new_invoice()
    
    
    # await update.message.reply_text(invoice_text, parse_mode='Markdown')