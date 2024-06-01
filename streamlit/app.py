from st_pages import Page, show_pages, add_page_title, hide_pages
from streamlit_extras.switch_page_button import switch_page
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import streamlit as st

st.set_page_config(page_title='PokéFinder')

st.header('Loading...')

show_pages(
    [
        Page("pages/home_page.py", "Home", icon=":house:"),
        Page("pages/functional_page.py", "Functional", icon=":iphone:"),
        Page("pages/registration_page.py", "Register a new user")
    ]
)

st.switch_page('pages/home_page.py')