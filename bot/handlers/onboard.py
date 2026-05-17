# # bot/handlers/onboard.py
# from telegram.ext import ConversationHandler
# from telethon import TelegramClient
# from telethon.sessions import StringSession
# from telethon.errors import SessionPasswordNeededError

# WAITING_PHONE, WAITING_OTP, WAITING_2FA = range(3)

# async def onboard_start(update, context):
#     await update.message.reply_text("Enter your phone number (e.g. +6591234567):")
#     return WAITING_PHONE

# async def onboard_phone(update, context):
#     phone = update.message.text.strip()
#     context.user_data["phone"] = phone

#     # Spin up a temporary client just for auth
#     client = TelegramClient(StringSession(), API_ID, API_HASH)
#     await client.connect()
#     await client.send_code_request(phone)
#     context.user_data["temp_client"] = client  # keep alive during conversation

#     await update.message.reply_text("Enter the OTP you received:")
#     return WAITING_OTP

# async def onboard_otp(update, context):
#     client = context.user_data["temp_client"]
#     phone = context.user_data["phone"]
#     try:
#         await client.sign_in(phone, update.message.text.strip())
#     except SessionPasswordNeededError:
#         await update.message.reply_text("Enter your 2FA password:")
#         return WAITING_2FA

#     session_string = client.session.save()
#     await client.disconnect()

#     # Persist to Supabase
#     db.table("user_sessions").upsert({
#         "telegram_user_id": update.effective_user.id,
#         "session_string": session_string,
#         "phone_number": phone,
#     }).execute()

#     await update.message.reply_text("✅ You're connected! Use /forward to get started.")
#     return ConversationHandler.END