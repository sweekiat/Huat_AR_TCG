from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db

async def invoice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /invoice command"""
    user_id = update.effective_user.id
    
    # Get invoice data from database
    invoice_data = db.get_user_invoice_data(user_id)
    
    if not invoice_data:
        await update.message.reply_text("No invoice data found. Please make sure you have claimed items first.")
        return
    
    # Generate invoice text (customize based on your needs)
    invoice_text = "📄 **Your Invoice**\n\n"
    total = 0
    
    for item in invoice_data:
        item_name = item.get('item_name', 'Unknown Item')
        price = item.get('price', 0)
        quantity = item.get('quantity', 1)
        subtotal = price * quantity
        total += subtotal
        
        invoice_text += f"• {item_name} x{quantity} - ${price:.2f} each = ${subtotal:.2f}\n"
    
    invoice_text += f"\n**Total: ${total:.2f}**"
    
    await update.message.reply_text(invoice_text, parse_mode='Markdown')