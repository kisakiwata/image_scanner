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
from retail_config import specific_source

# page config
st.set_page_config(page_title="Image Scanning and Product Identification", layout="wide")

# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("models/research/style/style.css")

# ---- HEADER SECTION ----
with st.container():
    st.subheader("Image Scanning and Product Identification")
    st.title("Integrate fast and reliable Image Scanning into your mobile apps and websites")
    st.write(
        "Get started with your trusted partner!"
    )
    #st.write("[Learn More >](https://pythonandvba.com)")

# Markdown
st.markdown("Input Image")

# File uploader
uploaded_file = st.file_uploader("Upload a file", type=["jpg", "png"])
if uploaded_file is not None:
    st.write("Image uploaded!")
    st.image(uploaded_file, caption=None, width=1200, use_column_width=None, clamp=False, channels="RGB", output_format="auto")

# Interactive Widgets
# st.subheader("Interactive Widgets")
# number = st.number_input("Enter a number", min_value=0, max_value=100, value=50)
# st.write("You entered:", number)

# # Button
# if st.button("Click me"):
#     st.write("Button clicked!")

# # Checkbox
# checkbox = st.checkbox("Check this box")
# if checkbox:
#     st.write("Checkbox is checked")

# Radio buttons
# radio_option = st.radio("Choose an option", ["Amazon", "Trader Joe's", "Walmart", "Costco", "Wholefoods"])
# st.write("You selected:", radio_option)


# Display JSON
st.subheader("Product Information")
json_directory = r"/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/webscrape_result/"
json_data = retrieve_json(json_directory)


# Selectbox 
selected_options = st.multiselect("Filter by retail", specific_source, key="product_brand_1") #, default=specific_source
st.write("You selected:", [value for value in selected_options])



# Check if selected options exist in the JSON data
# if selected_options:
    
#     filtered_data = {option: json_data.get(option, {}) for key, option in selected_options.items()}
#     df = pd.DataFrame(filtered_data)


# Dataframe
df = pd.DataFrame(json_data)

# Filter the original DataFrame to only include rows with the selected colors
df_filtered = df[df['product_brand_1'].isin(selected_options)]

#convert dataframe to adgrid
gb = GridOptionsBuilder.from_dataframe(df_filtered)
gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
gb.configure_side_bar() #Add a sidebar
gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
gridOptions = gb.build()

# grid_response = AgGrid(
#     df,
#     gridOptions=gridOptions,
#     data_return_mode='AS_INPUT', 
#     update_mode='MODEL_CHANGED', 
#     fit_columns_on_grid_load=False,
#     #theme='light', #Add theme color to the table
#     enable_enterprise_modules=True,
#     height=350, 
#     width='100%',
#     reload_data=True
# )

# #data = grid_response['data']
# selected = grid_response[selected_options] 
# df_grid = pd.DataFrame(data)


# Display the DataFrame using ag-Grid
st.subheader("Filtered Data")
if not df.empty:
    gb = GridOptionsBuilder.from_dataframe(df_filtered)
    grid_response = AgGrid(df_filtered, gridOptions=gb.build(), width="100%", height=400)
else:
    st.write("No data found for the selected options:", selected_options)



#with st.spinner('Wait for it...'):
    #time.sleep(5)

#st.dataframe(df_grid)
#st.json(json_data)



# Table
#st.table(df)

# ---- CONTACT ----
with st.container():
    st.write("---")
    st.header("Contact us")
    st.write("##")

    # Documention: https://formsubmit.co/ !!! CHANGE EMAIL ADDRESS !!!
    contact_form = """
    <form action="https://formsubmit.co/watanabekisaki@gmail.com" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="Your name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your message here" required></textarea>
        <button type="submit">Send</button>
    </form>
    """
    left_column, right_column = st.columns(2)
    with left_column:
        st.markdown(contact_form, unsafe_allow_html=True)
    with right_column:
        st.empty()