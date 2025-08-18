# from telegram import Update
# from telegram.ext import ContextTypes
# from bot.database.supabase_client import db
# from datetime import datetime

# from bot.util.admin_wrapper import admin_required

# @admin_required
# async def approve_invoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle /approve_invoice command"""
#     tba_invoices = db.get_tba_invoices()
#     if not tba_invoices:
#         await update.message.reply_text("You haven't claimed any items yet!")
#         return
    
#     # Format the items list
#     for i, item in enumerate(tba_invoices, 1):
        
    
#     await update.message.reply_text()