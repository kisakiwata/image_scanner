import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from web_scraping import retrieve_json

# Title
st.title("Image Scanning and Product Identification")

# Text
# st.text("Input Image")

# Markdown
st.markdown("Input Image")

# File uploader
uploaded_file = st.file_uploader("Upload a file", type=["jpg", "png"])
if uploaded_file is not None:
    st.write("Image uploaded!")
    st.image(uploaded_file, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")

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

# Selectbox
select_option = st.selectbox("Choose an option", ["Amazon", "Trader Joe's", "Walmart", "Costco", "Wholefoods"])
st.write("You selected:", select_option)

# Display JSON
st.subheader("Product Information")
json_directory = r"/Users/kisaki/Desktop/Kisaki_Personal_Folder/fast_api_sandbox/models/research/webscrape_result/"
json_data = retrieve_json(json_directory)
#st.json(json_data)

# Dataframe
df = pd.DataFrame(json_data)
st.dataframe(df)

# Table
#st.table(df)