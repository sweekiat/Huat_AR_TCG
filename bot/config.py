import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
ADMIN_USER_IDS = list(map(int, os.getenv('ADMIN_USER_IDS', '').split(',')))

if not all([TELEGRAM_BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required environment variables")