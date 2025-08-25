from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db
from datetime import datetime, timedelta

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command"""
    user_id = update.effective_user.id
    
    # Get user's claimed items from database
    items = db.get_user_items(user_id)
    print(items)
    
    if not items:
        await update.message.reply_text("You haven't claimed any items yet!")
        return
    
    # Format the items list
    items_text = "Your claimed items:\n\n"
    total_price = 0.0
    for i, item in enumerate(items, 1):
        # Adjust these fields based on your database schema
        item_name = item.get('Cards', {}).get('card_name', 'Unknown Item')
        set_name = item.get('Cards', {}).get('set_name', 'Unknown Set')
        price = item.get('Listings', {}).get('price', 'Unknown Price') if item.get('discounted_price') is None else item.get('discounted_price')
        claim_date = item.get('created_at', 'Unknown Date')
        quantity = item.get('quantity', 1)
        # Format the date to a simpler format
        if claim_date and claim_date != 'Unknown Date':
            try:
                parsed_date = datetime.fromisoformat(claim_date.replace('Z', '+00:00'))
                # Convert to Singapore time (UTC+8)
                singapore_date = parsed_date.replace(tzinfo=None) + timedelta(hours=8)
                # Format to readable string
                claim_date = singapore_date.strftime('%Y-%m-%d %H:%M')
            except:
                # Keep original if parsing fai
                pass
        items_text += f"{i}. {item_name}, {set_name} (claimed: {claim_date}) x {quantity}\n"
        items_text += f"   Price: {price}\n"
        total_price += (float(price) if isinstance(price, (int, float)) else 0.0 ) * quantity

    items_text += f"\nTotal Price: ${total_price}\n"
    items_text += "\nUse /invoice to generate your invoice."
    
    await update.message.reply_text(items_text)