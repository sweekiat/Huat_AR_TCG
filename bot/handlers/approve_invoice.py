from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    CallbackQueryHandler,
    filters
)
import asyncio
from bot.database.supabase_client import db

# Conversation states
REVIEWING_INVOICE = 1

class InvoiceApprovalHandler:
    def __init__(self, db):
        self.db = db
    
    async def approve_invoices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the invoice approval process"""
        # Get all non-approved invoices
        invoices = self.db.get_tba_invoices()
        
        if not invoices:
            await update.message.reply_text("No invoices pending approval.")
            return ConversationHandler.END
        
        # Store invoices in context for navigation
        context.user_data['invoices'] = invoices
        context.user_data['current_index'] = 0
        
        # Show first invoice
        await self.show_invoice(update, context, 0)
        return REVIEWING_INVOICE
    
    async def show_invoice(self, update: Update, context: ContextTypes.DEFAULT_TYPE, index: int):
        """Display an invoice with approval options"""
        invoices = context.user_data['invoices']
        
        if index >= len(invoices):
            await update.effective_message.reply_text("All invoices reviewed!")
            return ConversationHandler.END
        
        invoice = invoices[index]
        context.user_data['current_index'] = index
        
        # Create message text with invoice details
        message_text = f"""
📋 **Invoice #{invoice.get('id')}**
💰 Amount: ${invoice.get('amount', 'N/A')}
📅 Date: {invoice.get('created_at', 'N/A')}
🏷️ Claims: {invoice.get('claims', 'N/A')}

Invoice {index + 1} of {len(invoices)}
        """
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{invoice['id']}"),
                InlineKeyboardButton("⏭️ Skip", callback_data="skip")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send photo with caption if picture URL exists
        if invoice.get('picture'):
            try:
                if update.callback_query:
                    # If this is from a callback query, edit the message
                    await update.callback_query.message.delete()
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=invoice['picture'],
                        caption=message_text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    # If this is the first message
                    await update.message.reply_photo(
                        photo=invoice['picture'],
                        caption=message_text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
            except Exception as e:
                # If photo fails, send as text message
                print(f"Error sending photo: {e}")
                if update.callback_query:
                    await update.callback_query.edit_message_text(
                        text=f"⚠️ Could not load image\n{message_text}",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_text(
                        text=f"⚠️ Could not load image\n{message_text}",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
        else:
            # No picture, send as text
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text=message_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    text=message_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
    
    async def handle_approval_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks for approval/skip/cancel"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        current_index = context.user_data.get('current_index', 0)
        invoices = context.user_data.get('invoices', [])
        
        if data.startswith("approve_"):
            # Extract invoice ID and approve it
            invoice_id = int(data.split("_")[1])
            current_invoice = invoices[current_index]
            
            # Approve the invoice
            result = self.db.approve_invoice(invoice_id)
            
            if result:
                # Create claim invoices if claims exist
                if current_invoice.get('claims'):
                    self.db.create_claim_invoice(invoice_id, current_invoice['claims'])
                
                await query.edit_message_text(
                    f"✅ Invoice #{invoice_id} approved successfully!"
                )
                
                # Wait a moment then show next invoice
                await asyncio.sleep(1)
                next_index = current_index + 1
                if next_index < len(invoices):
                    await self.show_invoice(update, context, next_index)
                    return REVIEWING_INVOICE
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="🎉 All invoices reviewed! Approval process complete."
                    )
                    return ConversationHandler.END
            else:
                await query.edit_message_text(
                    f"❌ Error approving invoice #{invoice_id}. Please try again."
                )
                return ConversationHandler.END
        
        elif data == "skip":
            # Move to next invoice
            next_index = current_index + 1
            if next_index < len(invoices):
                await self.show_invoice(update, context, next_index)
                return REVIEWING_INVOICE
            else:
                await query.edit_message_text("🎉 All invoices reviewed!")
                return ConversationHandler.END
        
        elif data == "cancel":
            await query.edit_message_text("❌ Invoice approval cancelled.")
            return ConversationHandler.END
        
        return REVIEWING_INVOICE
    
    async def cancel_approval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the approval process"""
        await update.message.reply_text("Invoice approval process cancelled.")
        return ConversationHandler.END

# Create the conversation handler
def create_approval_conversation_handler(db):
    handler = InvoiceApprovalHandler(db)
    
    return ConversationHandler(
        entry_points=[CommandHandler("approve_invoices", handler.approve_invoices_command, filters=filters.ChatType.PRIVATE)],
        states={
            REVIEWING_INVOICE: [
                CallbackQueryHandler(handler.handle_approval_callback)
            ]
        },
        fallbacks=[CommandHandler("cancel", handler.cancel_approval)],
        per_chat=True,
        per_user=True
    )

# You'll need to add this import at the top of your file
approval_conversation = create_approval_conversation_handler(db)