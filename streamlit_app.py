# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched
 
# Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")
 
# Input field for customer name
name_on_order = st.text_input('Name on Smoothie:')
st.write("The Name on your Smoothie will be", name_on_order)
 
# Connect to Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()
 
# Load fruits from FRUIT_OPTIONS table
fruit_rows = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
fruit_names = [row['FRUIT_NAME'] for row in fruit_rows]
 
# Multiselect fruit options
ingredient_list = st.multiselect("Choose up to 5 ingredients:", fruit_names)
 
# Build the ingredients string
ingredients_string = ""
if ingredient_list:
    ingredients_string = " ".join(ingredient_list)
    st.write("Your smoothie will have:", ingredients_string)
 
# Insert a new order
if ingredient_list and name_on_order:
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """
 
    st.write("SQL to run:", my_insert_stmt)
 
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
 
# --- Manage existing orders section ---
st.header("Update Order Status")
 
# Load existing orders
orders_df = session.table("smoothies.public.orders").to_pandas()
 
# Show orders in editable dataframe
editable_df = st.data_editor(orders_df, num_rows="dynamic")
 
# Button to save updates
if st.button("Save Updates"):
    # Convert editable_df (Pandas) back to Snowpark DataFrame
    edited_dataset = session.create_dataframe(editable_df)
 
    # Original dataset from ORDERS table
    og_dataset = session.table("smoothies.public.orders")
 
    # Merge updates
    og_dataset.merge(
        edited_dataset,
        (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID']),
        [
            when_matched().update({
                "ORDER_FILLED": edited_dataset["ORDER_FILLED"]
            })
        ]
    )
 
    st.success("Order updates saved!", icon="✅")
