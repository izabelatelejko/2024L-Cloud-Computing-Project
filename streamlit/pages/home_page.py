import streamlit as st
import streamlit_authenticator as stauth
import yaml
import pandas as pd
import random
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
else:
    register_button = sideb.button("Register new user")
    if register_button:
        switch_page('register a new user')

#https://fontmeme.com/permalink/240530/1ebf16cfa649ebd03d7b91152d61ddb5.png
left, mid, right = st.columns([1, 7, 1])
with mid: 
    st.image('pokefinder.png')

st.header("Welcome to PokéFinder, your best app to find out what Pokémon are near you!")

col1, col2 = st.columns(2)
with col1:
    st.link_button("Pokémon GO", "https://pokemongolive.com/", use_container_width=True)
with col2:
    st.link_button("Bulbapedia", "https://bulbapedia.bulbagarden.net/wiki/Main_Page", use_container_width=True)

st.subheader("What *is* PokéFinder?")

st.write("PokéFinder is a webapp which allows you to check what Pokémon might spawn near your location in Pokémon GO.")

st.write("It utilises machine learning (kind of AI) to predict the Pokémon which will appear based on the time, date, your location, weather and other information.")

st.subheader("How to use it?")

st.write("First, log in or register using the form on the sidebar. Then, you can go and use the Functional page! While using the bronze user tier is free, if you want to access all of the more powerful models, there's a paid gold tier membership.")

st.write("Just provide us information about your location and the weather, choose a model, which will make the prediction, and poof! You'll be able to see the Pokémon most likely to appear in your area. PokéFinder **does not** save this data or use it for further training, it's only used for your prediction.")

if st.button("Go to the Functional page and get your predictions!", use_container_width=True):
    st.switch_page("pages/functional_page.py")

columns = st.columns(3)
pokemon_data = pd.read_csv('pokemon_urls_names.csv')
names = pokemon_data[pokemon_data['id'].isin(random.sample(list(pokemon_data['id']), 3))].reset_index()['name']

with columns[0]:
    st.image(f'poke_img/{names[0]}.jpg')

with columns[1]:
    st.image(f'poke_img/{names[1]}.jpg')

with columns[2]:
    st.image(f'poke_img/{names[2]}.jpg')


st.write("*All Pokémon designs are the property of the Pokémon Company. The images used in this application were downloaded from Bulbapedia.*")