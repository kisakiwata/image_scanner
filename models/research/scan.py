import sys
import subprocess
import time

# as inference.py requires protobuf==3.19.*, now force reinstalling the updated version
#subprocess.run("pip install --upgrade --force-reinstall protobuf", shell=True)

# add this arg to see latest results?
#subprocess.run("python models/research/process.py", shell=True)

import sys
#sys.path.append('/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/web_scraping.py')

import streamlit as st
import pandas as pd
from web_scraping import retrieve_json
import requests
import streamlit as st
import time
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
#from helper_function import location_on_click
from pyzipcode import ZipCodeDatabase
import os

# Create a flag to track whether the code has already been executed
code_executed = False

# Function to run the code
def run_code_once():
    global code_executed  # Use the global flag
    if not code_executed:
        subprocess.run([f"{sys.executable}", "models/research/process.py"])
        code_executed = True


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
image_directory = os.path.join(dirname,'images')
if uploaded_file is not None:
        with open(os.path.join(image_directory, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.read())
        st.write("Image uploaded!")
        st.image(uploaded_file, caption=None, width=1200, use_column_width=None, clamp=False, channels="RGB", output_format="auto")

# run the inference and web scraping with this

# Create a button
button_clicked = st.button("Ready to scan the image?")

# Check if the button is clicked
if button_clicked:
    #run_code_once()
    subprocess.run([f"{sys.executable}", "models/research/helper_function.py", f"{location}"])
    st.write("Products getting identified...")

    with st.spinner('Detecting the products and finding the information...'):
        time.sleep(10)
        st.success('Done!')

# Display JSON
json_directory = os.path.join(dirname,'webscrape_result')
json_files = [os.path.join(json_directory, filename) for filename in os.listdir(json_directory) if filename.endswith('.json')]
most_recent_json_file = max(json_files, key=os.path.getmtime)
print(most_recent_json_file)


if most_recent_json_file:
    json_modification_time = os.path.getmtime(most_recent_json_file)
    print(json_modification_time)
    # Get the most recent image modification time
    image_extensions = ('.jpg', '.jpeg', '.png')
    image_files = [os.path.join(image_directory, filename) for filename in os.listdir(image_directory) if filename.lower().endswith(image_extensions)]    
    if image_files:
        most_recent_image_file = max(image_files, key=os.path.getmtime)
        most_recent_image_time = os.path.getmtime(most_recent_image_file)
        print(most_recent_image_file)
        print(most_recent_image_time)
        if most_recent_image_time < json_modification_time:
            data_ready = True
        else:
            data_ready = False
else:
    data_ready = False
    
if data_ready:
    st.subheader("Product Information")
    json_data = retrieve_json(json_directory)

    # Dataframe
    df = pd.DataFrame(json_data)
    if not df.empty:
        new_cols = ['product_id','product_name',  'in_stock', 'product_brand_1', 'product_brand_2',
            'product_category_1', 'product_category_2', 'product_category_3',
            'product_review_rating_count', 'product_review_stars', 'product_price', 
            'product_dimensions', 'product_item_weight', 'product_unit',
            'store_location_zipcode', 'store_location_state', 'store_location_city',
            'store_id', 'product_link', 'brand_link', 'inventory_stockLevel',
            'tcin']
        selected_cols = [col for col in new_cols if col in df.columns]
        df = df[selected_cols]
        df = df.rename(columns={'product_brand_1': 'retail', 'product_brand_2': 'brand'})
        df = df.drop_duplicates(subset=["product_id"])
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
else:
    # Display a loading indicator
    st.subheader("Product Information (Loading...)")
    progress_bar = st.progress(0)

    # Simulate loading by updating the progress bar
    for i in range(100):
        time.sleep(0.1)
        progress_bar.progress(i + 1)

    st.success('Data is ready!')