import pandas as pd
# got this by running the script and sending it to chatgpt
set_dictionary = {
    "sv4m": "Future Flash",                     # Japanese Scarlet & Violet expansion
    "sv9": "Battle Partners",                 # Japanese Scarlet & Violet expansion
    "sv8": "Super Electric Breaker",           # Japanese Scarlet & Violet expansion
    "sv1a": "Triplet Beat",                    # Japanese Scarlet & Violet expansion
    "sv9a": "Heat Wave Arena",                   # Japanese Scarlet & Violet expansion
    "sv2a": "Pokemon Card 151",                # Japanese Scarlet & Violet expansion
    "sv3a": "Raging Surf",                    # Japanese Scarlet & Violet enhanced expansion
    "sv6a": "Night Wanderer",                 # Japanese Scarlet & Violet enhanced expansion
    "sv2d": "Clay Burst",                     # Japanese Scarlet & Violet expansion
    "sv1s": "Scarlet ex",                     # Japanese Scarlet & Violet main expansion (Scarlet ex)
    "sv10": "Glory of Team Rocket",                # Japanese Scarlet & Violet expansion
    "sv3": "Ruler of the Black Flame",        # Japanese Scarlet & Violet expansion
    "s12a": "VSTAR Universe",                 # Japanese Sword & Shield high class / subset
    "sv5m": "Cyber Judge",                    # Japanese Scarlet & Violet expansion
    "sv1v": "Violet ex",                      # Japanese Scarlet & Violet main expansion (Violet ex)
    "s8b": "VMAX Climax",                     # Japanese Sword & Shield high class pack
    "s10a": "Dark Phantasma",                 # Japanese Sword & Shield enhanced expansion
    "sv7a": "Paradise Dragona",               # Japanese Scarlet & Violet enhanced expansion
    "sv5a": "Crimson Haze",                   # Japanese Scarlet & Violet expansion
    "sv6": "Mask of Change",                  # Japanese Scarlet & Violet expansion
    "sv5k": "Wild Force",                    # Japanese Scarlet & Violet expansion
    "s11a": "Incandescent Arcana",            # Japanese Sword & Shield expansion
    "s9a": "Battle Region",                  # Japanese Sword & Shield expansion
    "sv4a": "Shiny Treasure ex",              # Japanese Scarlet & Violet high-class pack
    "sv2p": "Snow Hazard",                   # Japanese Scarlet & Violet expansion (paired with Clay Burst)
}

# Read the CSV file
df = pd.read_csv('inventory.csv')

# Split the card_code column and create new columns
df[['set_code', 'card_number']] = df['card_code'].str.split('-', expand=True)


# used to create dictionary from set_code
# unique_set_codes = df['set_code'].unique()  # Get unique set codes
# set_dictionary = {code: "" for code in unique_set_codes}
# # Write set_dictionary to text file
# with open('set_dictionary.txt', 'w') as f:
#     for key, value in set_dictionary.items():
#         f.write(f"'{key}': {value}\n")

