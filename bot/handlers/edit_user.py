from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot.database.supabase_client import db

# Define conversation states
WAITING_FOR_CHOICE = 1
WAITING_FOR_CONTACT = 2
WAITING_FOR_ADDRESS = 3

async def edit_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /edit_user command - show current user data"""
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not user_data:
        await update.message.reply_text("❌ User data not found. Please register first.")
        return ConversationHandler.END
    
    # Store current data
    context.user_data['current_user_data'] = user_data
    context.user_data['changes'] = {}
    
    # Show current info
    current_contact = user_data.get('contact_number', 'Not set')
    current_address = user_data.get('address', 'Not set')
    
    user_info_text = (
        f"👤 **Your Current Information**\n\n"
        f"📞 Contact Number: `{current_contact}`\n"
        f"📍 Address: `{current_address}`\n\n"
        f"What would you like to edit?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📞 Edit Phone Number", callback_data="edit_contact"),
            InlineKeyboardButton("📍 Edit Address", callback_data="edit_address")
        ],
        [
            InlineKeyboardButton("✅ Save Changes", callback_data="save_changes"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(user_info_text, reply_markup=reply_markup, parse_mode='Markdown')
    return WAITING_FOR_CHOICE

async def handle_edit_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses and show typing prompts"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "edit_contact":
        # PROMPT USER TO TYPE NEW PHONE NUMBER
        current_contact = context.user_data['current_user_data'].get('contact_number', 'Not set')
        
        await query.edit_message_text(
            f"📞 **Edit Phone Number**\n\n"
            f"Current number: `{current_contact}`\n\n"
            f"💬 **Please type your new phone number:**\n"
            f"Examples: +65 12345678 or 12345678\n\n"
            f"Type /cancel to go back.",
            parse_mode='Markdown'
        )
        return WAITING_FOR_CONTACT
    
    elif query.data == "edit_address":
        # PROMPT USER TO TYPE NEW ADDRESS
        current_address = context.user_data['current_user_data'].get('address', 'Not set')
        
        await query.edit_message_text(
            f"📍 **Edit Address**\n\n"
            f"Current address: `{current_address}`\n\n"
            f"💬 **Please type your new address:**\n"
            f"📮 **This is used for tracked mailing**\n"
            f"Example: Rivervale drive block 281D, Singapore 123456\n\n"
            f"Type /cancel to go back.",
            parse_mode='Markdown'
        )
        return WAITING_FOR_ADDRESS
    
    elif query.data == "save_changes":
        changes = context.user_data.get('changes', {})
        
        if not changes:
            await query.edit_message_text("❌ No changes were made.")
            context.user_data.clear()
            return ConversationHandler.END
        
        # Save to database
        user_id = update.effective_user.id
        success = db.edit_user(user_id, user_object=changes)
        
        if success:
            changes_text = "\n".join([f"• {key.replace('_', ' ').title()}: {value}" for key, value in changes.items()])
            await query.edit_message_text(
                f"✅ **Profile Updated Successfully!**\n\n"
                f"Changes saved:\n{changes_text}"
            )
        else:
            await query.edit_message_text("❌ Failed to update profile. Please try again.")
        
        context.user_data.clear()
        return ConversationHandler.END
    
    elif query.data == "cancel_edit":
        await query.edit_message_text("❌ Edit cancelled.")
        context.user_data.clear()
        return ConversationHandler.END

async def receive_new_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the NEW PHONE NUMBER typed by user"""
    new_contact = update.message.text.strip()
    
    # Basic validation
    if len(new_contact) < 8:
        await update.message.reply_text(
            "❌ Please provide a valid phone number (at least 8 digits).\n"
            "Try again or type /cancel to go back."
        )
        return WAITING_FOR_CONTACT
    
    # Store the new phone number
    context.user_data['changes']['contact_number'] = new_contact
    
    await update.message.reply_text(
        f"✅ **Phone number updated!**\n"
        f"New number: {new_contact}\n\n"
        f"Returning to main menu..."
    )
    
    # Show the updated menu
    await show_updated_menu(update, context)
    return WAITING_FOR_CHOICE

async def receive_new_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the NEW ADDRESS typed by user"""
    new_address = update.message.text.strip()
    
    # Basic validation
    if len(new_address) < 10:
        await update.message.reply_text(
            "❌ Please provide a complete address (at least 10 characters).\n"
            "Include street, city, and postal code.\n"
            "Try again or type /cancel to go back."
        )
        return WAITING_FOR_ADDRESS
    
    # Store the new address
    context.user_data['changes']['address'] = new_address
    
    await update.message.reply_text(
        f"✅ **Address updated!**\n"
        f"New address: {new_address}\n\n"
        f"Returning to main menu..."
    )
    
    # Show the updated menu
    await show_updated_menu(update, context)
    return WAITING_FOR_CHOICE

async def show_updated_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the menu again with updated information"""
    current_data = context.user_data['current_user_data']
    changes = context.user_data['changes']
    
    # Get current or new values
    contact = changes.get('contact_number', current_data.get('contact_number', 'Not set'))
    address = changes.get('address', current_data.get('address', 'Not set'))
    
    # Mark what's been changed
    contact_status = " 🆕" if 'contact_number' in changes else ""
    address_status = " 🆕" if 'address' in changes else ""
    
    user_info_text = (
        f"👤 **Your Information**\n\n"
        f"📞 Phone: `{contact}`{contact_status}\n"
        f"📍 Address: `{address}`{address_status}\n\n"
    )
    
    if changes:
        user_info_text += f"📝 **{len(changes)} change(s) pending**\n\n"
    
    user_info_text += "What would you like to do next?"
    
    keyboard = [
        [
            InlineKeyboardButton("📞 Edit Phone Number", callback_data="edit_contact"),
            InlineKeyboardButton("📍 Edit Address", callback_data="edit_address")
        ],
        [
            InlineKeyboardButton("✅ Save Changes", callback_data="save_changes"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(user_info_text, reply_markup=reply_markup, parse_mode='Markdown')

async def cancel_edit_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the edit process"""
    context.user_data.clear()
    await update.message.reply_text("❌ Edit cancelled.")
    return ConversationHandler.END

# Create the conversation handler
edit_user_conversation = ConversationHandler(
    entry_points=[CommandHandler('edit_user', edit_user_command, filters=filters.ChatType.PRIVATE)],
    states={
        WAITING_FOR_CHOICE: [
            CallbackQueryHandler(handle_edit_choice, pattern="^(edit_contact|edit_address|save_changes|cancel_edit)$")
        ],
        WAITING_FOR_CONTACT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_contact)
        ],
        WAITING_FOR_ADDRESS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_address)
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel_edit_user)],
    per_message=False,  # Important for webhook mode
    per_chat=False,     # Important for webhook mode
    per_user=True 
)