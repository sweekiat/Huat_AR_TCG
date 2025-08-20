# import logging
# from telegram import Update
# from telegram.ext import Application, CommandHandler
# from bot.config import TELEGRAM_BOT_TOKEN
# from bot.handlers.add_listing import add_listing_command
# from bot.handlers.debugger import debug_all_messages
# from bot.handlers.edit_user import edit_user_conversation
# from bot.handlers.start import start_command
# from bot.handlers.list import list_command
# from bot.handlers.invoice import invoice_conversation
# from bot.handlers.claim import claim_command
# from bot.handlers.external_invoice import external_invoice_command
# from telegram.ext import MessageHandler, filters

# from bot.handlers.unclaim import unclaim_command

# # Enable logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# def main():
#     """Start the bot"""
#     # Create the Application
#     application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
#     # Create the conversation handler
    
#     # Add command handlers
#     application.add_handler(CommandHandler("start", start_command))
#     application.add_handler(CommandHandler("list", list_command))
#     application.add_handler(edit_user_conversation) 
#     application.add_handler(invoice_conversation)
#     application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^claim(\s+\d+)?$'), claim_command))
#     application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^unclaim(\s+\d+)?$'), unclaim_command))
#     application.add_handler(CommandHandler("external_invoice", external_invoice_command)) 
#     application.add_handler(CommandHandler("add_listing", add_listing_command)) 
#     # application.add_handler(MessageHandler(filters.ALL, debug_all_messages))
#     # do i need a yours command handler? so that i can change and alter the claim amount

#     # Start the bot
#     logger.info("Starting Huat_AR_tcg bot...")
#     application.run_polling(allowed_updates=Update.ALL_TYPES)

# if __name__ == '__main__':
#     main()

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.add_listing import add_listing_command
from bot.handlers.debugger import debug_all_messages
from bot.handlers.edit_user import edit_user_conversation
from bot.handlers.start import start_command
from bot.handlers.list import list_command
from bot.handlers.invoice import invoice_conversation
from bot.handlers.claim import claim_command
from bot.handlers.external_invoice import external_invoice_command
from bot.handlers.unclaim import unclaim_command

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global application variable (initialized once per Cloud Function instance)
application = None

def get_application():
    """Get or create the bot application"""
    global application
    if application is None:
        logger.info("Initializing Telegram bot application...")
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add all your handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("list", list_command))
        application.add_handler(edit_user_conversation) 
        application.add_handler(invoice_conversation)
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^claim(\s+\d+)?$'), claim_command))
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^unclaim(\s+\d+)?$'), unclaim_command))
        application.add_handler(CommandHandler("external_invoice", external_invoice_command)) 
        application.add_handler(CommandHandler("add_listing", add_listing_command))
        # Uncomment if needed for debugging
        # application.add_handler(MessageHandler(filters.ALL, debug_all_messages))
        
        logger.info("Bot application initialized successfully!")
    
    return application

def telegram_webhook(request):
    """
    Cloud Function entry point for handling Telegram webhooks
    This function will be called every time someone sends a message to your bot
    """
    try:
        # Parse the incoming request
        if request.method != 'POST':
            return 'Only POST method allowed', 405
            
        update_data = request.get_json()
        if not update_data:
            logger.warning("Received empty request body")
            return 'No data received', 400
        
        # Get the bot application
        app = get_application()
        
        # Convert the JSON data to a Telegram Update object
        print(update_data)
        update = Update.de_json(update_data, app.bot)
        if not update:
            logger.warning("Could not parse update from JSON")
            return 'Invalid update format', 400
        
        # Process the update asynchronously
        # Cloud Functions require us to run async code in a sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(app.process_update(update))
        finally:
            loop.close()
        
        logger.info(f"Successfully processed update: {update.update_id}")
        return 'OK', 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return f'Error: {str(e)}', 500

def set_webhook(request):
    """
    Optional: Cloud Function to set the webhook URL
    Call this once after deploying to set up the webhook
    """
    try:
        webhook_url = request.get_json().get('webhook_url')
        if not webhook_url:
            return 'webhook_url required in JSON body', 400
            
        app = get_application()
        
        # Set the webhook
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(app.bot.set_webhook(url=webhook_url))
            logger.info(f"Webhook set to: {webhook_url}")
            return f'Webhook successfully set to {webhook_url}', 200
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error setting webhook: {str(e)}", exc_info=True)
        return f'Error setting webhook: {str(e)}', 500
