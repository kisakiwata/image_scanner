import streamlit as st
import os


# page config
st.set_page_config(page_title="Contact", layout="wide", initial_sidebar_state="expanded")


# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Directory to store URLs
dirname = os.path.dirname(__file__)
style_file = os.path.join(dirname, '..', 'style/style.css')
print(style_file)
local_css(style_file)


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