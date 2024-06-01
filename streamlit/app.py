import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# st.set_page_config(layout="wide")


def add_user_to_gold():
    users["credentials"]["usernames"][st.session_state["username"]]["tier"] = "gold"
    with open("users.yaml", "w") as file:
        yaml.dump(users, file, default_flow_style=False)


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


with open("users.yaml") as file:
    users = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    users["credentials"],
    users["cookie"]["name"],
    users["cookie"]["key"],
    users["cookie"]["expiry_days"],
)

authenticator.login()

if st.session_state["authentication_status"]:
    st.write(f"Welcome, *{st.session_state['name']}*!")
    if (
        users["credentials"]["usernames"][st.session_state["username"]]["tier"]
        == "gold"
    ):
        images = [
            "https://archives.bulbagarden.net/media/upload/0/05/0005Charmeleon.png",
            "https://archives.bulbagarden.net/media/upload/d/d2/0023Ekans.png",
            "https://archives.bulbagarden.net/media/upload/1/14/0116Horsea.png",
            "https://archives.bulbagarden.net/media/upload/5/54/0007Squirtle.png",
            "https://archives.bulbagarden.net/media/upload/4/4a/0025Pikachu.png",
        ]
        names = ["Charmeleon", "Ekans", "Horsea", "Squirtle", "Pikachu"]
        st.image(
            images,
            caption=names,
            width=200,
        )
        st.caption("Images from Bulbapedia")
    else:
        st.write("Sorry, you are poor, no pokemon for you :(")
        if st.button("Pay 100$"):
            add_user_to_gold()
            st.write(
                "Congratulations! You advanced to the golden tier! Please refresh your page"
            )
    authenticator.logout(location="sidebar")
elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
    register_user()
elif st.session_state["authentication_status"] is None:
    register_user()
