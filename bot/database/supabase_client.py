from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def get_user_items(self, user_id: int):
        """Get all claimed items for a user"""
        try:
            response = self.client.table('Claims').select('*').eq('user_id', user_id).eq('paid',False).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching user items: {e}")
            return []
    
    def check_user_exists(self, user_id: int):
        """Check if user record exists"""
        try:
            # Check if user exists
            existing = self.client.table('Users').select('*').eq('user_id', user_id).execute()
            return bool(existing.data)
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
    def create_user(self, user_id: int):
        """Create a new user record"""
        try:
            response = self.client.table('Users').insert({
                'user_id': user_id,
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
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
    def add_claim(self, user_id: int, card_code: str, quantity: int = 1):
        """Add a claim for a user"""
        try:
            response = self.client.table('Claims').insert({
                'user_id': user_id,
                'quantity': quantity,  
                'card_code': card_code
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error adding claim: {e}")
            return None
    def create_new_invoice(self):
        """Create a new invoice"""
        try:
            # This is a placeholder - adjust based on your invoice creation logic
            response = self.client.table('Invoices').insert({
                'user_id': 1,  # Example user_id, replace with actual logic
                'amount': 0.0  # Placeholder amount
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error creating new invoice: {e}")
            return None
    def get_listing(self, listing_id: int):
        """Get a specific listing by ID"""
        try:
            response = self.client.table('Listings').select('*').eq('id', listing_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching listing: {e}")
            return None
    def add_listing(self, card_code: str, listed_quantity: int, price: float):
        """Add a new listing"""
        try:
            response = self.client.table('Listings').insert({
                'card_code': card_code,
                'listed_quantity': listed_quantity,
                'price': price
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error adding listing: {e}")
            return None
# Initialize global database client
db = SupabaseClient()
