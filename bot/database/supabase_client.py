from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def get_user_items(self, user_id: int):
        """Get all claimed items for a user"""
        try:
            response = self.client.table('claims').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching user items: {e}")
            return []
    
    def user_exists(self, user_id: int, username: str = None, first_name: str = None):
        """Check if user record exists"""
        try:
            # Check if user exists
            existing = self.client.table('Users').select('*').eq('user_id', user_id).execute()
            return bool(existing.data)
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
    
    def get_user_invoice_data(self, user_id: int):
        """Get invoice data for a user"""
        try:
            # This is a placeholder - adjust based on your invoice logic
            response = self.client.table('invoices').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching invoice data: {e}")
            return []

# Initialize global database client
db = SupabaseClient()
