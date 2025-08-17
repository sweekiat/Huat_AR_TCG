from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot.database.supabase_client import db

# Define conversation states
WAITING_FOR_DELIVERY_CHOICE = 1
WAITING_FOR_ADDRESS = 2
WAITING_FOR_PICTURE = 3

async def invoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /invoice command - start the process"""
    user_id = update.effective_user.id
    claims = db.get_user_items(user_id)
    if not claims:
        await update.message.reply_text("❌ You have no claims to invoice.")
        return ConversationHandler.END
        
    invoice_text = "📄 **Your Invoice**\n\n"
    total = 0
    for item in claims:
        item_name = item.get('Cards', {}).get('card_name', 'Unknown Item')
        price = item.get('Listings', {}).get('price', 0)
        quantity = item.get('quantity', 1)
        subtotal = price * quantity
        total += subtotal
        
        invoice_text += f"• {item_name} x{quantity} - ${price:.2f} each = ${subtotal:.2f}\n"
    
    invoice_text += f"\n**Total: ${total:.2f}**"
    
    # Store invoice data in context for later use
    context.user_data['invoice_text'] = invoice_text
    context.user_data['total'] = total
    context.user_data['claims'] = claims
    
    # Send invoice
    await update.message.reply_text(invoice_text, parse_mode='Markdown')
    
    # Ask about delivery with buttons
    keyboard = [
        [
            InlineKeyboardButton("🚚 Yes, I need delivery", callback_data="delivery_yes"),
            InlineKeyboardButton("🏪 No, pickup only", callback_data="delivery_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚚 **Delivery Option**\n\n"
        "Do you need delivery for this order?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_DELIVERY_CHOICE

async def handle_delivery_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the delivery choice from inline buttons"""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query
    
    if query.data == "delivery_yes":
        context.user_data['needs_delivery'] = True
        await query.edit_message_text(
            "🚚 **Delivery Selected**\n\n"
            "📍 Please type your delivery address:"
        )
        return WAITING_FOR_ADDRESS
        
    elif query.data == "delivery_no":
        context.user_data['needs_delivery'] = False
        context.user_data['delivery_address'] = None
        
        await query.edit_message_text("🏪 **Pickup Selected** - No delivery needed")
        
        # Skip to picture request
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📸 Please send a picture to complete your invoice submission.\n\n"
                 "Send /cancel to cancel this process."
        )
        return WAITING_FOR_PICTURE

async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the address input"""
    address = update.message.text.strip()
    
    if len(address) < 10:  # Basic validation
        await update.message.reply_text(
            "❌ Please provide a complete address with at least 10 characters.\n"
            "Include street, city, and postal code."
        )
        return WAITING_FOR_ADDRESS
    
    # Store the address
    context.user_data['delivery_address'] = address
    
    await update.message.reply_text(
        f"✅ **Address Saved**\n\n"
        f"📍 Delivery to: {address}\n\n"
        f"📸 Now please send a picture to complete your invoice submission.\n\n"
        f"Send /cancel to cancel this process."
    )
    
    return WAITING_FOR_PICTURE

async def receive_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the picture sent by user"""
    if update.message.photo:
        # Get the highest resolution photo
        photo = update.message.photo[-1]
        
        # Get stored invoice data
        invoice_text = context.user_data.get('invoice_text', '')
        total = context.user_data.get('total', 0)
        claims = context.user_data.get('claims', [])
        needs_delivery = context.user_data.get('needs_delivery', False)
        delivery_address = context.user_data.get('delivery_address', None)
        
        # Build confirmation message
        confirmation_text = (
            f"✅ **Invoice submitted successfully!**\n\n"
            f"📸 Picture: Received\n"
            f"💰 Total: ${total:.2f}\n"
        )
        
        if needs_delivery:
            confirmation_text += f"🚚 Delivery: Yes\n📍 Address: {delivery_address}\n"
        else:
            confirmation_text += f"🏪 Delivery: No (Pickup)\n"
        
        confirmation_text += f"\nYour invoice has been processed."
        
        await update.message.reply_text(confirmation_text, parse_mode='Markdown')
        
        # Optional: Save to database with all info
        invoice_data = {
            'user_id': update.effective_user.id,
            'claims': claims,
            'photo_file_id': photo.file_id,
            'total': total,
            'needs_delivery': needs_delivery,
            'delivery_address': delivery_address
        }
        # db.save_complete_invoice(invoice_data)
        
        # Clear user data
        context.user_data.clear()
        
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "❌ Please send a picture, not text or other media.\n"
            "Send /cancel to cancel this process."
        )
        return WAITING_FOR_PICTURE

async def cancel_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the invoice process"""
    context.user_data.clear()
    await update.message.reply_text("❌ Invoice process cancelled.")
    return ConversationHandler.END

# Updated conversation handler with new states
invoice_conversation = ConversationHandler(
    entry_points=[CommandHandler('invoice', invoice_command)],
    states={
        WAITING_FOR_DELIVERY_CHOICE: [
            CallbackQueryHandler(handle_delivery_choice, pattern="^delivery_")
        ],
        WAITING_FOR_ADDRESS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address)
        ],
        WAITING_FOR_PICTURE: [
            MessageHandler(filters.PHOTO, receive_picture),
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_picture),  # Handle non-photo messages
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel_invoice)],
    # per_message=True,  # Add this line
    # per_chat=True,     # Add this line (optional but recommended)
    # per_user=True,     # Add this line (optional but recommended)
)