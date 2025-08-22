from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.database.supabase_client import db
from datetime import datetime
from bot.util.admin_wrapper import admin_required

@admin_required
async def approve_invoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve_invoice command"""
    tba_invoices = db.get_tba_invoices()
    if not tba_invoices:
        await update.message.reply_text("No invoices to approve")
        return
    
    # Store invoices in user_data for navigation
    context.user_data['invoices'] = tba_invoices
    context.user_data['current_invoice_index'] = 0
    
    # Show the first invoice
    await show_invoice(update, context, 0)

async def show_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    """Display a specific invoice with approval options"""
    invoices = context.user_data.get('invoices', [])
    
    if index < 0 or index >= len(invoices):
        await update.message.reply_text("No more invoices to review.")
        return
    
    invoice = invoices[index]
    context.user_data['current_invoice_index'] = index
    
    # Format invoice information
    invoice_text = format_invoice_info(invoice, index + 1, len(invoices))
    
    # Create inline keyboard
    keyboard = create_invoice_keyboard(index, len(invoices))
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get picture URL if available
    picture_url = invoice.get('picture', "")
    
    try:
        if picture_url:
            ##### Picture URL is already the public path, but if there isnt a way to store the url immediately already into invoices table,
            ##### then we need to use below
            # picture_url = db.client.storage.from_('Invoice_picture').get_public_url(picture_path)
            
            # Send photo with caption and keyboard
            if update.callback_query:
                # If this is from a callback query, edit the message
                await update.callback_query.message.delete()
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=picture_url,
                    caption=invoice_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                # If this is the initial command
                await update.message.reply_photo(
                    photo=picture_url,
                    caption=invoice_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
        else:
            # No picture available, send text only
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text=invoice_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    text=invoice_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
    except Exception as e:
        # Fallback to text if image fails to load
        error_text = f"{invoice_text}\n\n⚠️ <i>Failed to load invoice picture</i>"
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=error_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                text=error_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

def format_invoice_info(invoice, current_num, total_num):
    """Format invoice information for display"""
    invoice_id = invoice.get('id', 'N/A')
    amount = invoice.get('amount', 'N/A')
    description = invoice.get('description', 'No description')
    created_at = invoice.get('created_at', '')
    user_id = invoice.get('user_id', 'N/A')
    
    # Format date if available
    formatted_date = 'N/A'
    if created_at:
        try:
            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        except:
            formatted_date = created_at
    
    return f"""
📋 <b>Invoice {current_num} of {total_num}</b>

🆔 <b>ID:</b> {invoice_id}
💰 <b>Amount:</b> ${amount}
📝 <b>Description:</b> {description}
👤 <b>User ID:</b> {user_id}
📅 <b>Created:</b> {formatted_date}
    """.strip()

def create_invoice_keyboard(current_index, total_invoices):
    """Create inline keyboard for invoice approval"""
    keyboard = []
    
    # Approval buttons
    keyboard.append([
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_invoice_{current_index}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_invoice_{current_index}")
    ])
    
    # Navigation buttons
    nav_buttons = []
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_invoice_{current_index}"))
    
    if current_index < total_invoices - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_invoice_{current_index}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Skip and exit buttons
    keyboard.append([
        InlineKeyboardButton("⏭️ Skip", callback_data=f"skip_invoice_{current_index}"),
        InlineKeyboardButton("🚪 Exit", callback_data="exit_invoice_review")
    ])
    
    return keyboard

async def handle_invoice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from invoice review"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    invoices = context.user_data.get('invoices', [])
    current_index = context.user_data.get('current_invoice_index', 0)
    
    if data.startswith('approve_invoice_'):
        index = int(data.split('_')[-1])
        await approve_invoice(update, context, index)
    
    elif data.startswith('reject_invoice_'):
        index = int(data.split('_')[-1])
        await reject_invoice(update, context, index)
    
    elif data.startswith('skip_invoice_'):
        index = int(data.split('_')[-1])
        # Move to next invoice
        next_index = index + 1
        if next_index < len(invoices):
            await show_invoice(update, context, next_index)
        else:
            await query.edit_message_text("✅ All invoices reviewed!")
    
    elif data.startswith('prev_invoice_'):
        index = int(data.split('_')[-1])
        prev_index = index - 1
        if prev_index >= 0:
            await show_invoice(update, context, prev_index)
    
    elif data.startswith('next_invoice_'):
        index = int(data.split('_')[-1])
        next_index = index + 1
        if next_index < len(invoices):
            await show_invoice(update, context, next_index)
    
    elif data == 'exit_invoice_review':
        await query.edit_message_text("👋 Invoice review session ended.")
        # Clear user data
        context.user_data.pop('invoices', None)
        context.user_data.pop('current_invoice_index', None)

async def approve_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    """Approve an invoice"""
    invoices = context.user_data.get('invoices', [])
    if index >= len(invoices):
        return
    
    invoice = invoices[index]
    invoice_id = invoice.get('id')
    
    try:
        # Update invoice status in database
        db.update_invoice_status(invoice_id, 'approved')
        
        # Remove from current list
        invoices.pop(index)
        context.user_data['invoices'] = invoices
        
        await update.callback_query.edit_message_text(
            f"✅ Invoice #{invoice_id} approved successfully!"
        )
        
        # Show next invoice if available
        if index < len(invoices):
            await show_invoice(update, context, index)
        elif invoices:
            await show_invoice(update, context, index - 1)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🎉 All invoices have been reviewed!"
            )
    except Exception as e:
        await update.callback_query.edit_message_text(
            f"❌ Error approving invoice: {str(e)}"
        )

async def reject_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
    """Reject an invoice"""
    invoices = context.user_data.get('invoices', [])
    if index >= len(invoices):
        return
    
    invoice = invoices[index]
    invoice_id = invoice.get('id')
    
    try:
        # Update invoice status in database
        db.update_invoice_status(invoice_id, 'rejected')
        
        # Remove from current list
        invoices.pop(index)
        context.user_data['invoices'] = invoices
        
        await update.callback_query.edit_message_text(
            f"❌ Invoice #{invoice_id} rejected."
        )
        
        # Show next invoice if available
        if index < len(invoices):
            await show_invoice(update, context, index)
        elif invoices:
            await show_invoice(update, context, index - 1)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🎉 All invoices have been reviewed!"
            )
    except Exception as e:
        await update.callback_query.edit_message_text(
            f"❌ Error rejecting invoice: {str(e)}"
        )

# Don't forget to add the callback handler to your application:
# application.add_handler(CallbackQueryHandler(handle_invoice_callback))