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
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, Bot
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
from pythonjsonlogger import jsonlogger

# Enable logging
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s'
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global application variable
application = None

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

async def error_handler(update, context):
    """Log the error and send a message to the user."""
    logger.error(
        "Exception while handling an update",
        extra={
            "error": str(context.error),
            "error_type": type(context.error).__name__,
            "update_id": update.update_id if update else None,
            "chat_id": update.effective_chat.id if update and update.effective_chat else None,
            "user_id": update.effective_user.id if update and update.effective_user else None,
            "message_text": update.effective_message.text if update and update.effective_message else None
        },
        exc_info=context.error
    )

    # Optional: send a friendly message to the user
    if update and update.effective_chat:
        await update.effective_chat.send_message(
            "Oops! Something went wrong. The bot owner has been notified."
        )

def get_application():
    """Get or create the bot application"""
    global application
    if application is None:
        logger.info("Initializing Telegram bot application...")
        
        # Create application without updater for webhook mode
        application = (
            Application.builder()
            .token(TELEGRAM_BOT_TOKEN)
            .updater(None)  # Disable updater for webhook mode
            .build()
        )
        application.add_error_handler(error_handler)

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

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    try:
        # Get the update data
        update_data = request.get_json()
        if not update_data:
            logger.warning("Received empty request body")
            return 'No data received', 400
        
        logger.info(f"Received update: {update_data}")
        
        # Get the bot application
        bot_app = get_application()
        
        # Convert JSON to Update object
        update = Update.de_json(update_data, bot_app.bot)
        if not update:
            logger.warning("Could not parse update from JSON")
            return 'Invalid update format', 400
        
        asyncio.run_coroutine_threadsafe(bot_app.process_update(update), loop)
        
        logger.info(f"Successfully processed update: {update.update_id}")
        return 'OK', 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return f'Error: {str(e)}', 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Set the webhook URL"""
    try:
        data = request.get_json()
        webhook_url = data.get('webhook_url') if data else None
        
        if not webhook_url:
            return jsonify({'error': 'webhook_url required in JSON body'}), 400
        
        # Create a simple bot instance for webhook management
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Set the webhook using asyncio.run
        async def set_webhook_async():
            await bot.set_webhook(url=webhook_url)
            await bot.initialize()  # Clean up
        
        # Use persistent loop instead of asyncio.run
        future = asyncio.run_coroutine_threadsafe(set_webhook_async(), loop)
        future.result() 
        
        logger.info(f"Webhook set to: {webhook_url}")
        return jsonify({'message': f'Webhook successfully set to {webhook_url}'}), 200
            
    except Exception as e:
        logger.error(f"Error setting webhook: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error setting webhook: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return 'Bot is healthy!', 200

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return 'Telegram Bot is running!', 200

# Initialize the application when the module is imported
get_application()

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)