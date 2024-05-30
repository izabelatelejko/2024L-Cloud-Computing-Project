from st_pages import Page, show_pages, add_page_title, hide_pages
from streamlit_extras.switch_page_button import switch_page
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import streamlit as st

def add_user_to_gold():
    users["credentials"]["usernames"][st.session_state["username"]]["tier"] = "gold"
    with open("users.yaml", "w") as file:
        yaml.dump(users, file, default_flow_style=False)

add_page_title()

show_pages(
    [
        Page("pages/home_page.py", "Home", icon=":house:"),
        Page("pages/functional_page.py", "Functional", icon=":iphone:"),
        Page("pages/registration_page.py", "Register a new user")
    ]
)

hide_pages(["Register a new user"])

with open("users.yaml") as file:
    users = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    users["credentials"],
    users["cookie"]["name"],
    users["cookie"]["key"],
    users["cookie"]["expiry_days"],
)

authenticator.login(location='sidebar')
sideb = st.sidebar

register_button = sideb.button("Register a new user")
if register_button:
    switch_page('register a new user')

if st.session_state["authentication_status"]:
    curr_tier = users["credentials"]["usernames"][st.session_state["username"]]["tier"]
    sideb.write(f"""Your current tier is: **{curr_tier}**.""")
    if curr_tier == 'bronze':
        sideb.button("Upgrade to **gold**", on_click=add_user_to_gold)
    authenticator.logout(location="sidebar")