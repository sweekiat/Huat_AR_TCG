from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, filters

def debug_all_messages(update: Update, context: CallbackContext):
    """Debug handler to see all incoming messages"""
    message = update.message
    
    print("=" * 50)
    print("INCOMING MESSAGE DEBUG:")
    print(f"Message ID: {message.message_id}")
    print(f"Chat ID: {message.chat.id}")
    print(f"Chat Type: {message.chat.type}")
    print(f"Chat Title: {getattr(message.chat, 'title', 'N/A')}")
    print(f"From User: {message.from_user.first_name} (@{message.from_user.username})")
    print(f"Message Text: {message.text}")
    print(f"Has Reply: {bool(message.reply_to_message)}")
    
    if message.reply_to_message:
        original = message.reply_to_message
        print(f"Reply to Message ID: {original.message_id}")
        print(f"Original Text: {original.text}")
        print(f"Original Caption: {original.caption}")
        print(f"Is Forwarded: {bool(original.forward_from_chat)}")
        print(f"Forward From Chat: {getattr(original.forward_from_chat, 'title', 'N/A')}")
        print(f"Is Automatic Forward: {getattr(original, 'is_automatic_forward', 'N/A')}")
        
        if original.text:
            first_line = original.text.split('\n')[0]
            print(f"First Line: {first_line}")
    
    print("=" * 50)

# Add this handler to catch ALL messages