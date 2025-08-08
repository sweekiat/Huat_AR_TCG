from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.supabase_client import db
from bot.config import ADMIN_USER_IDS

def admin_required(func):
    """Decorator to restrict commands to admin users"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id not in ADMIN_USER_IDS:
            await update.message.reply_text("❌ Admin access required.")
            return
        return await func(update, context)
    return wrapper