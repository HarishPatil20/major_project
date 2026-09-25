import streamlit as st
from streamlit_geolocation import streamlit_geolocation

from utils.weather_api import get_weather

st.set_page_config(
    page_title="Live Weather",
    page_icon="🌦️",
    layout="wide"
)

st.markdown(
    """
    <style>
    .weather-hero {
        background: linear-gradient(135deg, #164e63 0%, #0e7490 52%, #38bdf8 100%);
        color: white;
        padding: 28px 30px;
        border-radius: 22px;
        margin-bottom: 20px;
        box-shadow: 0 12px 28px rgba(14, 116, 144, 0.2);
    }
    .weather-hero h1 { margin: 0; font-size: clamp(28px, 4vw, 42px); }
    .weather-hero p { margin: 8px 0 0; opacity: 0.9; }
    .weather-location {
        background: #ecfeff;
        border: 1px solid #a5f3fc;
        border-radius: 16px;
        padding: 16px 18px;
        margin: 14px 0 20px;
        color: #155e75;
    }
    .weather-card {
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 18px;
        padding: 18px;
        min-height: 112px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
    }
    .weather-card-label { color: #64748b; font-size: 13px; }
    .weather-card-value { color: #0f172a; font-size: 26px; font-weight: 800; margin-top: 8px; }
    @media (max-width: 640px) {
        .weather-hero { padding: 22px; border-radius: 16px; }
        .weather-card { min-height: 96px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="weather-hero">
        <h1>🌦️ Live Weather</h1>
        <p>Local conditions, captured from your device location.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="weather-location">📍 Your browser will ask for permission to use your current location.</div>',
    unsafe_allow_html=True
)

location = streamlit_geolocation()

latitude = location.get("latitude") if location else None
longitude = location.get("longitude") if location else None

if latitude is None or longitude is None:
    st.info("Allow location access in your browser to load live weather.")

else:

    with st.spinner("Fetching weather for your location..."):

        weather = get_weather(
            latitude=float(latitude),
            longitude=float(longitude)
        )

    if weather["success"]:

        st.success(f"📍 Weather near {weather['city']}, {weather['country']}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f'<div class="weather-card"><div class="weather-card-label">🌡️ Temperature</div><div class="weather-card-value">{weather["temperature"]} °C</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="weather-card"><div class="weather-card-label">🤗 Feels Like</div><div class="weather-card-value">{weather["feels_like"]} °C</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="weather-card"><div class="weather-card-label">💧 Humidity</div><div class="weather-card-value">{weather["humidity"]} %</div></div>', unsafe_allow_html=True)

        with col2:
            st.markdown(f'<div class="weather-card"><div class="weather-card-label">🌬️ Wind Speed</div><div class="weather-card-value">{weather["wind_speed"]} m/s</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="weather-card"><div class="weather-card-label">🌤️ Condition</div><div class="weather-card-value">{weather["condition"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="weather-card"><div class="weather-card-label">📊 Pressure</div><div class="weather-card-value">{weather["pressure"]} hPa</div></div>', unsafe_allow_html=True)

        st.info(f"Description: {weather['description'].title()}")

        icon_url = f"https://openweathermap.org/img/wn/{weather['icon']}@2x.png"
        st.image(icon_url, width=110)

    else:
        st.error(weather["message"])