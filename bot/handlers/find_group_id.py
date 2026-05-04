from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db
from bot.util.admin_wrapper import admin_required

@admin_required
async def add_listing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add_listing command"""
    # Get listing data from command arguments
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /add_listing <card_code> <listed_quantity> <price>")
        return

    card_code = context.args[0]
    try:
        listed_quantity = int(context.args[1])
        price = float(context.args[2])
    except ValueError:
        await update.message.reply_text("Invalid quantity or price.")
        return

    # Add listing to database
    listing_data = db.add_listing(card_code, listed_quantity, price)
    if listing_data:
        await update.message.reply_text(f"Listing added successfully:\n #{listing_data['listing_id']}\n{listing_data['card']}\n{listing_data['card_code']}\nQty: {listing_data['listed_quantity']}\nPrice: ${listing_data['price']}")
    else:
        await update.message.reply_text("Failed to add listing.")
    
    