from supabase import create_client, Client
from bot.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY

class SupabaseClient:
    def __init__(self):
        # self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

#### Users Table ####
    def check_user_exists(self, user_id: int):
        """Check if user record exists"""
        try:
            # Check if user exists
            existing = (self.client.table("Users").select("*").eq("user_id", user_id).execute())
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
    def edit_user(self,user_id:int,user_object:dict):
        """Edit user record"""
        try:
            response = self.client.table('Users').update(user_object).eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error editing user: {e}")
            return None
    def get_user(self, user_id: int):
        """Get user record by ID"""
        try:
            response = self.client.table('Users').select('*').eq('user_id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

#### Listings Table ####
    def get_listings(self):
        """Get all listings from the database"""
        try:
            response = self.client.table('Listings').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Error fetching listings: {e}")
            return []
    def get_listing(self, listing_id: int):
        """Get a specific listing by ID"""
        try:
            response = self.client.table('Listings').select('*').eq('listing_id', listing_id).execute()
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
            card_info = self.client.table('Cards').select('*').eq('card_code', card_code).execute()
            if card_info.data:
                return {
                    **response.data[0],
                    'card': card_info.data[0]['card_name'] # or card_info.data[0]['card_name'] if you only want name
                }
            else:
                return response.data[0]
            
        except Exception as e:
            print(f"Error adding listing: {e}")
            return None

#### Claims Table ####
    def get_user_items(self, user_id: int):
        """Get all claimed items for a user"""
        try:
            # response = self.client.table('Claims').select('*').eq('user_id', user_id).eq('paid',False).execute()
            response = self.client.table('Claims').select('*, Cards(card_name, set_name), Listings(listing_id, price)').eq('user_id', user_id).eq('paid', False).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching user items: {e}")
            return []
    def get_claimed_quantity(self, listing_id: int):
        """Get total claimed quantity for a listing"""
        try:
            response = self.client.table('Claims').select("quantity").eq('listing_id', listing_id).execute()
            return sum(item['quantity'] for item in response.data) if response.data else 0
        except Exception as e:
            print(f"Error fetching claimed quantity: {e}")
            return 0
    def add_claim(self, user_id: int, card_code: str, quantity: int = 1, listing_id: str = None, discounted_price: float = None):
        """Add a claim for a user"""
        try:
            # Check if the user already has a claim for this card
            existing_claim = self.client.table('Claims').select('*').eq('user_id', user_id).eq('card_code', card_code).execute()
            if existing_claim.data:
                # If a claim exists, update the quantity
                current_quantity = existing_claim.data[0]['quantity']
                new_quantity = current_quantity + quantity
                response = self.client.table('Claims').update({'quantity': new_quantity}).eq('user_id', user_id).eq('card_code', card_code).execute()
                return response.data
            # If no claim exists, create a new one
            response = self.client.table('Claims').insert({
                'user_id': user_id,
                'quantity': quantity,  
                'card_code': card_code,
                'listing_id': listing_id,
                'discounted_price': discounted_price
            }).execute()
            return response.data
        except Exception as e:
            print(f"Error adding claim: {e}")
            return None

    def remove_claim(self, user_id: int, card_code: str, quantity: int = 0):
        """Remove a claim for a user"""
        response = None
        try:
            if quantity == 0:
                # If quantity is 0, remove all claims for this user and card_code
                response = self.client.table('Claims').delete().eq('user_id', user_id).eq('card_code', card_code).execute()
            else:
                # Get current claim to update quantity
                current_claim = self.client.table('Claims').select('*').eq('user_id', user_id).eq('card_code', card_code).execute()
                if current_claim.data:
                    current_quantity = current_claim.data[0]['quantity']
                    new_quantity = max(0, current_quantity - quantity)
                    if new_quantity == 0:
                        # Remove the claim if quantity becomes 0
                        response = self.client.table('Claims').delete().eq('user_id', user_id).eq('card_code', card_code).execute()
                    else:
                        # Update the quantity
                        response = self.client.table('Claims').update({'quantity': new_quantity}).eq('user_id', user_id).eq('card_code', card_code).execute()
                else:
                    return response
            return response
        except Exception as e:
            print(f"Error removing claim: {e}")
            return None
#### Invoices table ####
    def create_new_invoice(self, invoice_object: dict):
        """Create a new invoice"""
        try:
            # This is a placeholder - adjust based on your invoice creation logic
            response = self.client.table('Invoices').insert(
                {
                'user_id': invoice_object.get('user_id', 1),  # Example user_id, replace with actual logic
                'amount': invoice_object.get('amount', 0.0),  # Placeholder amount,
                'claims': invoice_object.get('claims', ""),
                'username': invoice_object.get('username', None),
                'picture': invoice_object.get('picture', None),
            }
            ).execute()
            return response.data
        except Exception as e:
            print(f"Error creating new invoice: {e}")
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
    def approve_invoice(self, invoice_id: int):
        """Approve an invoice"""
        try:
            response = self.client.table('Invoices').update({'approved': True}).eq('invoice_id', invoice_id).execute()
            return response.data
        except Exception as e:
            print(f"Error approving invoice: {e}")
            return None
    def get_tba_invoices(self):
        """Get all invoices"""
        try:
            response = self.client.table('Invoices').select('*').eq('approved', False).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching all invoices: {e}")
            return []
    def upload_image_to_storage(self, file_data: bytes, file_name: str, bucket_name: str = "images", content_type: str = "image/jpeg"):
        """Enhanced upload with content type"""
        try:
            result = result = self.client.storage.from_(bucket_name).upload(
    path=file_name,
    file=file_data,
    file_options={"content-type": content_type, "cache-control": "3600"},
)

            
            if result:
                public_url = self.client.storage.from_(bucket_name).get_public_url(file_name)
                return {
                    "success": True,
                    "file_name": file_name,
                    "public_url": public_url,
                    "storage_path": f"{bucket_name}/{file_name}"
                }
            else:
                return {"success": False, "error": "Upload failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    #### Claim_invoice table #####
    def create_claim_invoice(self,invoice_id:int,claims:str):
        try:
            claim_list = claims.split(",")  # Split the claims string into a list
            for claim in claim_list:
                # Create a new claim_invoice record for each claim
                response = self.client.table('Claim_invoice').insert({
                    'invoice_id': invoice_id,
                    'claim': claim.strip()  # Remove any extra spaces
                }).execute()
        except Exception as e:
            print(f"Error creating claim_invoice: {e}")
            return None
# Initialize global database client
db = SupabaseClient()
