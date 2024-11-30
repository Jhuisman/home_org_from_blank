import streamlit as st
import sqlite3

# Connect to SQLite database
DB_FILE = "lcm.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Ensure the categories table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")
conn.commit()

# Pre-fill database with default categories if empty
default_categories = ["Electronics", "Furniture", "Clothing", "Vehicles", "Other"]
for category in default_categories:
    cursor.execute("INSERT OR IGNORE INTO category (name) VALUES (?)", (category,))
conn.commit()

# Fetch categories from database
cursor.execute("SELECT name FROM category")
categories = [row[0] for row in cursor.fetchall()]

# Streamlit form for adding items
st.title("Add New Item")

with st.form("item_form"):
    name = st.text_input("Item Name")
    category = st.selectbox("Select a Category", categories + ["Add a New Category"])
    
    # If the user wants to add a new category
    new_category = None
    if category == "Add a New Category":
        new_category = st.text_input("New Category Name")
    
    purchase_date = st.date_input("Purchase Date")
    responsible_person = st.text_input("Responsible Person")
    status = st.selectbox("Status", ["Active", "Inactive"])
    submitted = st.form_submit_button("Add Item")

    if submitted:
        # Add new category to database if specified
        if new_category:
            cursor.execute("INSERT OR IGNORE INTO category (name) VALUES (?)", (new_category,))
            conn.commit()
            st.success(f"New category '{new_category}' added!")
        
        # Use the new category if provided, otherwise the selected one
        final_category = new_category if new_category else category

        # Insert the item into the database
        cursor.execute("""
        INSERT INTO item (name, category, purchase_date, responsible_person, status)
        VALUES (?, ?, ?, ?, ?)
        """, (name, final_category, purchase_date, responsible_person, status))
        conn.commit()
        st.success(f"Item '{name}' added successfully!")


st.title("View Items")
cursor.execute("SELECT * FROM item")
rows = cursor.fetchall()

if rows:
    import pandas as pd
    df = pd.DataFrame(rows, columns=["ID", "Name", "Category", "Purchase Date", "Responsible Person", "Status"])
    st.dataframe(df)
else:
    st.info("No items found in the database.")
