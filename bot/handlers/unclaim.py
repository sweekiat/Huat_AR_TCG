from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db

async def unclaim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle claim message (not command)"""
    print("Claim command triggered")
    user = update.effective_user
    message_text = update.message.text
    print(f"Received claim message from user {user.id}: {message_text}")
    user_exists = db.check_user_exists(user.id)
    if not user_exists:
        create_user_success = db.create_user(user.id)
        if not create_user_success:
            await update.message.reply_text("Failed to create user record. Please try again later.")
            return
        return

    if update.message.reply_to_message:
        original_message = update.message.reply_to_message
        first_line_of_message = original_message.text.split('\n')[0]
        print(f"Original message text: {first_line_of_message}")
        listing_number = first_line_of_message.strip("#")
        print(f"Extracted listing number: {listing_number}")
        if not listing_number.isdigit():
            await update.message.reply_text("No listing number found in the replied message.")
            return
        

        listing_details = db.get_listing(listing_number)
        if not listing_details:
            await update.message.reply_text("Listing not found.")
            return
        print(f"Listing details: {listing_details}")
        card_code = listing_details.get('card_code', 'Unknown Card')
        quantity = message_text.split()[-1] if message_text.split()[-1].isdigit() else 1  # Default to 1 if no quantity specified
        add_claim_response = db.remove_claim(user.id, card_code, quantity)
        if not add_claim_response:
            await update.message.reply_text("Failed to claim the card. Please try again later.")
            return
        
        
        await update.message.reply_text(f"✅ Detected reply to message: {card_code}")
    else:
        await update.message.reply_text("Please reply to a message to claim a card.")
        return
    
    print(f"User ID: {user.id}, Card Code: {card_code}")
