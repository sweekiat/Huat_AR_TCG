from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def get_user_items(self, user_id: int):
        """Get all claimed items for a user"""
        try:
            response = self.client.table('Claims').select('*').eq('user_id', user_id).execute()
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
            response = self.client.table('Invoices').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching invoice data: {e}")
            return []
    def get_listings(self):
        """Get all listings from the database"""
        try:
            response = self.client.table('Listings').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Error fetching listings: {e}")
            return []
    def add_claim(self, user_id: int, card_code: str):
        """Add a claim for a user"""
        try:
            response = self.client.table('Claims').insert({
                'user_id': user_id,
                'quantity': 1,  
                'card_code': card_code
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error adding claim: {e}")
            return None
# Initialize global database client
db = SupabaseClient()
