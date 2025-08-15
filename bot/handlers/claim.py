from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db

async def claim_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        first_line_of_message = original_message.text.split('\n')[0] if original_message.text else original_message.caption.split('\n')[0]
        print(f"Original message text: {first_line_of_message}")
        listing_id = first_line_of_message.strip("#")
        print(f"Extracted listing number: {listing_id}")
        if not listing_id.isdigit():
            await update.message.reply_text("Could not find a valid listing number in the replied message. This is a personal item.")
            return
        

        listing_details = db.get_listing(int(listing_id))
        if not listing_details:
            await update.message.reply_text("Listing not found.")
            return
        already_claimed_quantity = db.get_claimed_quantity(int(listing_id))
        print(f"Already claimed quantity: {already_claimed_quantity}")
        listed_quantity = listing_details.get('listed_quantity', 0)
        
        card_code = listing_details.get('card_code', 'Unknown Card')
        quantity = message_text.split()[-1] if message_text.split()[-1].isdigit() else 1  
        if already_claimed_quantity + quantity > listed_quantity:
            await update.message.reply_text("This listing has already been fully claimed.")
            return
        add_claim_response = db.add_claim(user.id, card_code, int(quantity), listing_id)
        if not add_claim_response:
            await update.message.reply_text(f"Failed to claim the card. Please try again later. {add_claim_response}")
            return
        
        
        await update.message.reply_text(f"✅ Successfully claimed: {card_code}")
    else:
        await update.message.reply_text("Please reply to a message to claim a card.")
        return
    
    print(f"User ID: {user.id}, Card Code: {card_code}")
