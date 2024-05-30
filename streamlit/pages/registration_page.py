import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from st_pages import hide_pages
from streamlit_extras.switch_page_button import switch_page

hide_pages(["Register a new user"])

def add_user_to_gold():
    users["credentials"]["usernames"][st.session_state["username"]]["tier"] = "gold"
    with open("users.yaml", "w") as file:
        yaml.dump(users, file, default_flow_style=False)

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

if st.session_state["authentication_status"]:
    curr_tier = users["credentials"]["usernames"][st.session_state["username"]]["tier"]
    sideb.write(f"""Your current tier is: **{curr_tier}**.""")
    if curr_tier == 'bronze':
        sideb.button("Upgrade to **gold**", on_click=add_user_to_gold)
    authenticator.logout(location="sidebar")

def register_user():
    try:
        (
            email_of_registered_user,
            username_of_registered_user,
            name_of_registered_user,
        ) = authenticator.register_user(pre_authorization=False, clear_on_submit=True)
        if email_of_registered_user:
            st.success("User registered successfully")
            users["credentials"]["usernames"][username_of_registered_user][
                "tier"
            ] = "bronze"
            with open("users.yaml", "w") as file:
                yaml.dump(users, file, default_flow_style=False)
    except Exception as e:
        st.error(e)

register_user()