import streamlit as st

st.set_page_config(layout="wide")
st.title("Hello, Streamlit on App Engine!")
st.write("This is a simple Streamlit app running on Google App Engine.")

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
