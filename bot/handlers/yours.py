from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db
from bot.util.admin_wrapper import admin_required

@admin_required
async def yours_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # """Handle yours command"""
    # # Get listing data from command arguments
    # if len(context.args) < 3:
    #     await update.message.reply_text("Usage: /yours <user> <price>")
    #     return
    # user = context.args[0]
    # try:
    #     price = float(context.args[1])
    # except ValueError:
    #     await update.message.reply_text("Invalid price.")
    #     return

    # # Add listing to database
    # listing_data = db.add_claim(card_code, listed_quantity, price)
    # if listing_data:
    #     await update.message.reply_text(f"Listing added successfully: {listing_data}")
    # else:
    #     await update.message.reply_text("Failed to add listing.")
    
    return