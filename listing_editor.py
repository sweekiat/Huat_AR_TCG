from bot.database.supabase_client import db
listings = db.get_listings_with_name()
print(listings[0])
with open("listings.txt", "w") as f:
    for listing in listings:
        f.write(f"#{listing.get('listing_id')}\n{listing.get('card_code')}\n{listing.get('Cards', {}).get('card_name', '')}\nQty: {listing.get('listed_quantity')}\nPrice: ${listing.get('price')}\n\n")
