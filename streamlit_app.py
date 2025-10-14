# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
 
 
# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("""Choose the fruits you want in your custom Smoothie!""")
 
cnx = st.connection("snowflake")
session = cnx.session()
 
name_on_order = st.text_input('Name On Smoothies:')
st.write('The Name on the smoothie will be: ', name_on_order)
 
 
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
 
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()
 
ingredients_list = st.multiselect(
    'Choose upto 5 ingredients: ',
    my_dataframe,
    max_selections=5,
)
 
 
if ingredients_list:
    #st.write(ingredients_list)
    #st.text(ingredients_list)
 
    ingredients_string =''
 
    for x in ingredients_list:
        ingredients_string += x +' ' 
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == x, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', x,' is ', search_on, '.')
        st.subheader(x + 'Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
 
    #st.write(ingredients_string)
 
    time_to_insert = st.button('Submit Order')
 
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
 
    #st.write(my_insert_stmt)
    #st.stop()
 
 
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
