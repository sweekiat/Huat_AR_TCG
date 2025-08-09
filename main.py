import logging
from telegram import Update
from telegram.ext import Application, CommandHandler
from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.add_listing import add_listing_command
from bot.handlers.start import start_command
from bot.handlers.list import list_command
from bot.handlers.invoice import invoice_command
from bot.handlers.claim import claim_command
from bot.handlers.external_invoice import external_invoice_command
from telegram.ext import MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("invoice", invoice_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^claim(\s+\d+)?$'), claim_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^unclaim(\s+\d+)?$'), unclaim_command))
    application.add_handler(CommandHandler("external_invoice", external_invoice_command)) 
    application.add_handler(CommandHandler("add_listing", add_listing_command)) 
    # do i need a yours command handler? so that i can change and alter the claim amount

    # Start the bot
    logger.info("Starting Huat_AR_tcg bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()