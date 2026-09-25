import streamlit as st
from utils.weather_api import get_weather

st.set_page_config(
    page_title="Live Weather",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Live Weather Information")

st.write("Enter a city name to view the current weather.")

city = st.text_input("🏙️ Enter City Name", placeholder="Example: Mangalore")

if st.button("Get Weather"):

    if city.strip() == "":
        st.warning("Please enter a city name.")

    else:

        with st.spinner("Fetching weather..."):

            weather = get_weather(city)

        if weather["success"]:

            st.success(f"Weather in {weather['city']}, {weather['country']}")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("🌡️ Temperature", f"{weather['temperature']} °C")
                st.metric("🤗 Feels Like", f"{weather['feels_like']} °C")
                st.metric("💧 Humidity", f"{weather['humidity']} %")

            with col2:
                st.metric("🌬️ Wind Speed", f"{weather['wind_speed']} m/s")
                st.metric("🌤️ Condition", weather["condition"])
                st.metric("📊 Pressure", f"{weather['pressure']} hPa")

            st.info(f"Description: {weather['description'].title()}")

            icon_url = f"https://openweathermap.org/img/wn/{weather['icon']}@2x.png"
            st.image(icon_url, width=100)

        else:
            st.error(weather["message"])