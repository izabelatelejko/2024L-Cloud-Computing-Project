import streamlit as st
import streamlit_authenticator as stauth
import numpy as np
import pandas as pd
import yaml
import requests
import time
import json
import re
from yaml.loader import SafeLoader
from streamlit_js_eval import get_geolocation
from datetime import datetime
from utils import decide_time_of_day
from streamlit_extras.switch_page_button import switch_page
from st_pages import hide_pages

hide_pages(["Register a new user"])

weather_api_key = 'cef44488cfa34d5db2182bff7f788d7d'

density_data = pd.read_csv('density_data.csv', sep=';', header=None, index_col=None)

def get_population_density(lat: float, lon: float):
    lat += 180
    lon += 90
    return density_data.iat[int(4*lon), int(4*lat)]

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

def update_weather_fields():
    if input_lat != 0 and input_lon != 0:
        r_weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={input_lat}&lon={input_lon}&appid={weather_api_key}").json()
        r_weather_main = r_weather["main"]
        r_weather_wind = r_weather["wind"]
        st.session_state.wind_speed = float(r_weather_wind["speed"])
        st.session_state.wind_dir = float(r_weather_wind["deg"])
        st.session_state.pressure = float(r_weather_main["pressure"])
        st.session_state.temperature = float(r_weather_main["temp"]) - 273.15
    else:
        st.write("Please provide latitude and longitude first.")

def get_available_models():
    r = requests.post(
        "https://europe-west3-cloud-computing-project-418718.cloudfunctions.net/serve-cf",
        headers={
            # "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json",
        },
        json={"request_type": "get_model_metrics"},
    )
    model_dict = json.loads(r.content)
    model_names = []
    model_metrics = []
    model_orig_names = []
    for key, value in model_dict.items():
        model_orig_names.append(key)
        model_metrics.append(int(value))
    model_ranks = np.argsort(model_metrics)
    model_orig_names = np.array(model_orig_names)
    model_orig_names = model_orig_names[model_ranks]

    i = 1
    for idx, model in enumerate(model_ranks):
        if idx >= len(model_ranks) - 1:
            model_names.append(f'Gold Model {i}')
            i += 1
        else:
            model_names.append(f'Bronze Model {idx + 1}')
    model_metrics.sort()

    st.session_state.model_names = model_names
    st.session_state.model_metrics = model_metrics
    st.session_state.model_orig_names = model_orig_names

def get_predictions(model_name: str, model_acc: int, request_json: dict):
    r = requests.post(
        "https://europe-west3-cloud-computing-project-418718.cloudfunctions.net/serve-cf",
        headers={
            # "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json",
        },
        json={"request_type": "get_model_prediction",
              "model_name": model_name,
              "model_accuracy": model_acc,
               "input": json.dumps(request_json)},
    )
    bin_list =  r.content
    return list(map(int, re.findall(r'\d+', bin_list.decode())))

time_of_day_dict = {
    "morning": 0, 
    "afternoon": 1, 
    "evening": 2, 
    "night": 3
}
day_of_week_dict_name_to_num = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}
day_of_week_dict_num_to_name = {
    0 :"Monday",
    1 :"Tuesday",
    2 :"Wednesday",
    3 :"Thursday",
    4 :"Friday",
    5 :"Saturday",
    6 :"Sunday"
}

urbanisation_dict = {
    'Rural': 0,
    'Midurban': 1,
    'Suburban': 2,
    'Urban': 3
}

terrain_type_dict = {
    'Water': 0,
    'Evergreen Needleleaf Forest': 1,
    'Evergreen Broadleaf Forest': 2,
    'Deciduous Needleleaf Forest': 3,
    'Deciduous Broadleaf Forest': 4,
    'Mixed Forest': 5,
    'Woodland': 6,
    'Wooded Grassland': 7,
    'Closed Shrubland': 8,
    'Open Shrubland': 9,
    'Grassland': 10,
    'Cropland': 11,
    'Bare Ground': 12,
    'Urban and Built': 13
}

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

if not st.session_state["authentication_status"]:
    register_button = sideb.button("Register a new user")
    if register_button:
        switch_page('register a new user')
    st.header("Please log into the application first.")
    st.stop()
else:
    curr_tier = users["credentials"]["usernames"][st.session_state["username"]]["tier"]
    sideb.write(f"""Your current tier is: **{curr_tier}**.""")
    if curr_tier == 'bronze':
        sideb.button("Upgrade to **gold**", on_click=add_user_to_gold)
    authenticator.logout(location="sidebar")
    st.header(f"Welcome to PokéFinder, **{st.session_state['name']}**!")
    with st.popover("How to use PokéFinder?"):
        st.write("First, accept the localisation prompt in your browser or input you longitude and latitude manually.")
        st.write("Then, make sure you select the correct data for the following boxes and sliders.")
        st.write("Now, only if you've already input latitude and longitude, press `Get more weather info for provided longitude and latitude`. It will fill the four boxes below with information about the places in coordinates you've provided.")
        st.write("Once all the information is given, press `Load avaliable models` button to see available models. Depending on your tier, you might not be able to choose some of them. The selection button next to them will be disabled, but you'll still be able to see them.")

location = get_geolocation()
time.sleep(0.5)
lat = location['coords']['latitude']
lon = location['coords']['longitude']

r = requests.get(f"https://api.sunrisesunset.io/json?lat={lat}&lng={lon}").json()['results']
curr_time = datetime.now()
curr_year = curr_time.year
curr_month = curr_time.month
curr_day = curr_time.day
curr_hour = curr_time.hour
curr_minute = curr_time.minute
current_date = curr_time.date()
sunrise_time = datetime.strptime(f"{current_date} {r['sunrise']}", "%Y-%m-%d %I:%M:%S %p")
sunset_time = datetime.strptime(f"{current_date} {r['sunset']}", "%Y-%m-%d %I:%M:%S %p")

min_from_sunrise = int((curr_time - sunrise_time).total_seconds() / 60)
min_to_sunset = -int((sunset_time - curr_time).total_seconds() / 60)

input_lat = st.number_input(label="Latitude",
              value=lat if lat is not None else 0)
input_lon = st.number_input(label="Longitude",
              value=lon if lon is not None else 0)
input_water = st.selectbox(label="Are you close (less than 100m) to water?",
                           options=("Yes", "No"))
input_terrain = st.selectbox(label="What kind of terrain are you in?",
                             options=list(terrain_type_dict.keys()))
input_urban = st.selectbox(label="How urbanised is the area you're in?",
                           options=list(urbanisation_dict.keys()))
input_poke_num = st.slider("How many Pokémon are near you?", 0, 15, 3)
input_pokestop_dist = st.slider("How many km are you from the nearest pokestop?", 0.0, 20.0, 1.0, step=0.1)
input_gym_dist = st.slider("How many km are you from the nearest gym?", 0.0, 20.0, 1.0, step=0.1)
pop_density = get_population_density(input_lat, input_lon)
input_density = st.number_input("What's the estimated population density of where you are now?",
                                value =  pop_density if lat != 0 and lon != 0 and pop_density != -9999.0 else 100)
# input_tod = st.text_input(label="Time of day",
#               value=decide_time_of_day(curr_hour))
# input_h = st.number_input(label="Current hour",
#               value=curr_hour)
# input_m = st.number_input(label="Current minute",
#               value=curr_minute)
# input_wd = st.selectbox(label="Current weekday",
#                         options=('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
#                         index=curr_time.weekday())

st.write("Current weather (select all applicable):")
st.checkbox("Rainy", key='rainy')
st.checkbox("Foggy", key='foggy')
st.checkbox("Windy", key='windy')
st.checkbox("Clear sky", key='clear_sky')
st.checkbox("Partly cloudy", key='partly_cloudy')
st.checkbox("Very cloudy", key='very_cloudy')

weather_button = st.button('Get more weather info for provided longitude and latitude', on_click=update_weather_fields)

input_wind_speed = st.number_input(label="Wind speed", key='wind_speed')
input_wind_dir = st.number_input(label="Wind direction (in degrees)", key='wind_dir')
input_pressure = st.number_input(label="Atmospheric pressure", key='pressure')
input_temperature = st.number_input(label="Temperature (in °C)", key='temperature')

request_json = {
    "latitude": float(input_lat),
    "longitude": float(input_lon),
    "appearedTimeOfDay": time_of_day_dict[str(decide_time_of_day(curr_hour))],
    "appearedHour": float(curr_hour),
    "appearedMinute": float(curr_minute),
    "appearedDayOfWeek": curr_time.weekday(),
    "appearedDay": curr_day,
    "appearedMonth": curr_month,
    "appearedYear": curr_year,
    "terrainType": terrain_type_dict[input_terrain],
    "closeToWater": 1 if input_water == 'Yes' else 0,
    "temperature": round(input_temperature, 2),
    "windSpeed": input_wind_speed,
    "windBearing": input_wind_dir,
    "pressure": input_pressure,
    "sunriseMinutesSince": min_from_sunrise,
    "sunsetMinutesBefore": min_to_sunset,
    "population_density": input_density,
    "gymDistanceKm": input_gym_dist,
    "pokestopDistanceKm": input_pokestop_dist,
    "n_poks_appeared": input_poke_num,
    "clear-night": 1 if st.session_state.clear_sky else 0,
    "cloudy": 1 if st.session_state.very_cloudy else 0,
    "fog": 1 if st.session_state.foggy else 0,
    "rain": 1 if st.session_state.rainy else 0,
    "wind": 1 if st.session_state.windy else 0,
    "urbanization_level": urbanisation_dict[input_urban],
    "partly-cloudy": 1 if st.session_state.partly_cloudy else 0
  }

st.header('Model selection')

if 'clicked' not in st.session_state:
    st.session_state.clicked = False
    st.session_state.disabled_load_model = False

load_models_button = st.button('Load available models', type="primary", disabled=st.session_state.disabled_load_model)
if load_models_button:
    get_available_models()
    st.session_state.clicked = True
    st.session_state.disabled_load_model = True


st.session_state.disable = (users["credentials"]["usernames"][st.session_state["username"]]["tier"] != 'gold')

if st.session_state.clicked:
    for i in range(len(st.session_state.model_names)):
        col1, col2, col3 = st.columns([2, 2, 1])
        model_name = st.session_state.model_names[i]
        model_metric = st.session_state.model_metrics[i]
        with col1:
            st.write(model_name)
        with col2:
            st.write(f"Accuracy: {model_metric}%")
        with col3:
            if not (st.session_state.disable and 'Gold' in model_name):
                if st.button('Select this model', key=model_name):
                    st.session_state.curr_model = model_name
            else:
                if st.button('You need to be **gold** tier to access this model',
                        disabled=True,
                        key=model_name):
                    st.session_state.curr_model = model_name
        
    st.text_input('#### Currently selected model', key='curr_model', disabled=True)

    poke_ids = []

    if 'predictions' not in st.session_state:
        st.session_state.predictions = False

    if st.session_state.curr_model != '':

        if st.button("Get prediction"):
            for i in range(len(st.session_state.model_names)):
                if str(st.session_state.model_names[i]) == (st.session_state.curr_model):
                    idx = i
                    break
            real_model_name = st.session_state.model_orig_names[idx]
            real_model_acc = st.session_state.model_metrics[idx]
            poke_ids = get_predictions(real_model_name, real_model_acc, request_json)
            st.session_state.predictions = True

        if st.session_state.predictions:
            if len(poke_ids) > 0:
                st.header(f'The {len(poke_ids)} Pokémon most likely to appear near you are:')

            pokemon_data = pd.read_csv('pokemon_urls_names.csv')
            poke_data = pokemon_data[pokemon_data['id'].isin(poke_ids)]
            poke_data['id'] = pd.Categorical(poke_data['id'], categories=poke_ids, ordered=True)
            poke_data = poke_data.sort_values('id')
            images = []
            names = []
            for id in poke_ids:
                images.append('poke_img/' + poke_data[poke_data['id'] == id]['name'].values[0] + '.jpg')
                names.append(poke_data[poke_data['id'] == id]['name'].values[0])
            st.image(
                images,
                caption=names,
                width=200
            )

