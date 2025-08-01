import streamlit as st
import pandas as pd
import os

# Title of the app
st.title("Card Price Calculator")

# Input field for card price
card_price = st.number_input("Enter card price ($):", min_value=0.0, format="%.2f")

# Input field for card name (optional)
card_name = st.text_input("Card name (optional):")

# Button to add the price
if st.button("Add Card Price"):
    if card_price > 0:
        # Calculate total price: card_price + $30 + $8 + 9%
        subtotal = card_price + 30 + 8
        total_price = subtotal * 1.09
        
        # Create new row
        new_row = {
            'card_name': card_name if card_name else f"Card_{len(pd.read_csv('prices.csv') if os.path.exists('prices.csv') else pd.DataFrame()) + 1}",
            'original_price': card_price,
            'total_price': round(total_price, 2)
        }
        
        # Save to CSV
        if os.path.exists('prices.csv'):
            df = pd.read_csv('prices.csv')
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])
        
        df.to_csv('prices.csv', index=False)
        st.success(f"Added! Total price: ${round(total_price, 2)}")
    else:
        st.error("Please enter a valid price greater than 0")

# Display current data
if os.path.exists('prices.csv'):
    st.subheader("Stored Prices:")
    df = pd.read_csv('prices.csv')
    st.dataframe(df)
    
    # Show grand total
    if not df.empty:
        grand_total = df['total_price'].sum()
        st.subheader(f"Grand Total: ${round(grand_total, 2)}")