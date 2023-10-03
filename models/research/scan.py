import sys
import subprocess

# as inference.py requires protobuf==3.19.*, now force reinstalling the updated version
#subprocess.run("pip install --upgrade --force-reinstall protobuf", shell=True)

# add this arg to see latest results?
#subprocess.run("python models/research/process.py", shell=True)

import sys
#sys.path.append('/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/web_scraping.py')

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from web_scraping import retrieve_json
import requests
import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image
import time
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
#from retail_config import specific_source
from pyzipcode import ZipCodeDatabase
import os


# page config
st.set_page_config(page_title="Home", layout="wide", initial_sidebar_state="expanded")


# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Directory to store URLs
dirname = os.path.dirname(__file__)
style_file = os.path.join(dirname,'style/style.css')
print(style_file)
local_css(style_file)



# ---- HEADER SECTION ----
with st.container():

    left_column, right_column = st.columns(2)
    with left_column:
        st.header("Image Scan for Quick Product Identification")
        st.subheader("Integrate into your mobile apps and websites")
    with right_column:
        logo = os.path.join(dirname, '..', 'Image_scanner.png')
        st.image(logo, width=100)

    #st.write("[Learn More >](https://pythonandvba.com)")

# Markdown
st.markdown("Input Image")

with st.sidebar:
    # Selectbox 
    st.markdown("Input Location")
    location = st.text_input('Zipcode:', '94117')
    zcdb = ZipCodeDatabase()
    city_state = zcdb[location].city + ", " + zcdb[location].state
    st.write('Current search location is', city_state)

# File uploader
uploaded_file = st.file_uploader("Upload a file", type=["jpg", "png", "jpeg"])
dirname = os.path.dirname(__file__)
iamge_directory = os.path.join(dirname,'images')
if uploaded_file is not None:
        with open(os.path.join(iamge_directory, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.read())
        st.write("Image uploaded!")
        st.image(uploaded_file, caption=None, width=1200, use_column_width=None, clamp=False, channels="RGB", output_format="auto")

# run the inference and web scraping with this
subprocess.run("python models/research/process.py", shell=True)

# Display JSON
st.subheader("Product Information")
json_directory = os.path.join(dirname,'webscrape_result')
json_data = retrieve_json(json_directory)


# Dataframe
df = pd.DataFrame(json_data)
cols = df.columns
if not df.empty:
    new_cols = ['product_id','product_name',  'in_stock', 'product_brand_1', 'product_brand_2',
        'product_category_1', 'product_category_2', 'product_category_3',
        'product_review_rating_count', 'product_review_stars', 'product_price', 
        'product_dimensions', 'product_item_weight', 'product_unit',
        'store_location_zipcode', 'store_location_state', 'store_location_city',
        'store_id', 'product_link', 'brand_link', 'inventory_stockLevel',
        'tcin']
    df = df[new_cols]
    df = df.rename(columns={'product_brand_1': 'retail', 'product_brand_2': 'brand'})
    selected_options = st.multiselect("Filter by retail", list(set(df["retail"]))) #, default=specific_source

    # Filter the original DataFrame to only include rows with the selected colors
    df_filtered = df[df['retail'].isin(selected_options)]

    #convert dataframe to adgrid
    gb = GridOptionsBuilder.from_dataframe(df_filtered)
    gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    gridOptions = gb.build()

    gb = GridOptionsBuilder.from_dataframe(df_filtered)
    grid_response = AgGrid(df_filtered, gridOptions=gb.build(), width="100%", height=400,
    data_return_mode='AS_INPUT', 
    update_mode='MODEL_CHANGED', 
    fit_columns_on_grid_load=False,)
else:
    st.write("No data found")

#st.subheader("Filtered Data")

#else:
    #st.write("No data found for the selected options:", selected_options)

# # ---- CONTACT ----
# with st.container():
#     st.write("---")
#     st.header("Contact us")
#     st.write("##")

#     # Documention: https://formsubmit.co/ !!! CHANGE EMAIL ADDRESS !!!
#     contact_form = """
#     <form action="https://formsubmit.co/watanabekisaki@gmail.com" method="POST">
#         <input type="hidden" name="_captcha" value="false">
#         <input type="text" name="name" placeholder="Your name" required>
#         <input type="email" name="email" placeholder="Your email" required>
#         <textarea name="message" placeholder="Your message here" required></textarea>
#         <button type="submit">Send</button>
#     </form>
#     """
#     left_column, right_column = st.columns(2)
#     with left_column:
#         st.markdown(contact_form, unsafe_allow_html=True)
#     with right_column:
#         st.empty()