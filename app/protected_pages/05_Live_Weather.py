import os
import base64
import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from utils.weather_api import get_weather, get_auto_location
from utils.theme import apply_premium_theme

apply_premium_theme()


@st.cache_data(show_spinner=False)
def _get_weather_icon_data_uri():
    icon_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "assets",
        "weather_icon.jpg",
    )
    try:
        if os.path.exists(icon_path):
            with open(icon_path, "rb") as icon_file:
                encoded = base64.b64encode(icon_file.read()).decode("ascii")
                return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        pass
    return ""


_weather_icon_uri = _get_weather_icon_data_uri()

st.markdown(
    """
    <style>
    .stApp { background: #f4f6f0; }
    .weather-hero {
        background: linear-gradient(135deg, #1E5620 0%, #2D7D32 50%, #0284C7 100%);
        color: white;
        padding: 30px clamp(20px, 4vw, 42px);
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 12px 32px rgba(30, 86, 32, 0.2);
    }
    .weather-hero h1 { margin: 0; font-size: clamp(28px, 4vw, 42px); font-weight: 800; }
    .weather-hero p { margin: 8px 0 0; color: #F5F5DC; font-size: 15px; }
    
    .weather-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .weather-card {
        background: #ffffff;
        border: 1px solid #dce9de;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
        transition: transform 0.2s ease;
    }
    .weather-card:hover { transform: translateY(-2px); }
    .weather-label { color: #6D4C41; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .weather-val { color: #1E5620; font-size: 32px; font-weight: 850; margin-top: 8px; }

    .city-picker {
        background: #ffffff;
        border: 1px solid #dce9de;
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    
    iframe[title="streamlit_geolocation.streamlit_geolocation"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

_weather_icon_html = (
    f'<img src="{_weather_icon_uri}" style="width:56px; height:56px; border-radius:14px; '
    f'box-shadow:0 6px 16px rgba(0,0,0,0.2); flex-shrink:0;" />'
    if _weather_icon_uri
    else ""
)

st.markdown(
    f"""
    <div class="weather-hero" style="display:flex; align-items:center; gap:16px;">
        {_weather_icon_html}
        <div>
            <h1 style="margin:0;">🌦️ Live Agricultural Weather Advisory</h1>
            <p style="margin:6px 0 0;">Real-time microclimate conditions, humidity, wind, and irrigation advisories.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

CITY_COORDS = {
    "Mangalore (Mangaluru / Dakshina Kannada)": (12.9141, 74.8560),
    "Udupi": (13.3409, 74.7421),
    "Chikmagalur": (13.3161, 75.7720),
    "Madikeri / Coorg": (12.4244, 75.7382),
    "Karwar (Uttara Kannada)": (14.8058, 74.1305),
    "Bangalore (Urban/Rural)": (12.9716, 77.5946),
    "Mysore": (12.2958, 76.6394),
    "Mandya": (12.5218, 76.8951),
    "Shimoga": (13.9299, 75.5681),
    "Davanagere": (14.4644, 75.9218),
    "Tumkur": (13.3409, 77.1006),
    "Belgaum": (15.8497, 74.4977),
    "Hassan": (13.0033, 76.1004),
    "Kolar": (13.1367, 78.1292),
}

# Auto-detect location with city fallback options
col_loc1, col_loc2 = st.columns([3, 1])

with col_loc1:
    selected_city = st.selectbox(
        "📍 District / Region Weather Station",
        ["Auto-Detected Location"] + list(CITY_COORDS.keys()),
        index=0
    )

with col_loc2:
    st.write("")
    st.write("")
    location = streamlit_geolocation()

if selected_city == "Auto-Detected Location":
    lat, lon, source_label = get_auto_location(location)
else:
    coord_key = selected_city if selected_city in CITY_COORDS else "Mangalore (Mangaluru / Dakshina Kannada)"
    lat, lon = CITY_COORDS[coord_key]
    source_label = selected_city

weather = get_weather(latitude=float(lat), longitude=float(lon))

if weather.get("success"):
    st.success(f"📍 **Weather Station:** {weather['city']}, {weather['country']} (Lat {lat:.2f}, Lon {lon:.2f}) — *{source_label}*")
    
    w1, w2, w3 = st.columns(3)
    with w1:
        st.markdown(f'<div class="weather-card"><div class="weather-label">🌡️ Temperature</div><div class="weather-val">{weather["temperature"]} °C</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="weather-card"><div class="weather-label">🤗 Feels Like</div><div class="weather-val">{weather["feels_like"]} °C</div></div>', unsafe_allow_html=True)

    with w2:
        st.markdown(f'<div class="weather-card"><div class="weather-label">💧 Humidity</div><div class="weather-val">{weather["humidity"]} %</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="weather-card"><div class="weather-label">🌬️ Wind Speed</div><div class="weather-val">{weather["wind_speed"]} m/s</div></div>', unsafe_allow_html=True)

    with w3:
        st.markdown(f'<div class="weather-card"><div class="weather-label">🌤️ Condition</div><div class="weather-val" style="font-size:24px;">{weather["condition"]}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="weather-card"><div class="weather-label">📊 Pressure</div><div class="weather-val">{weather["pressure"]} hPa</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_adv, col_icon = st.columns([4, 1])
    with col_adv:
        st.markdown(
            f"""
            <div style="background:#ffffff; border:1px solid #dce9de; border-left:5px solid #1E5620; border-radius:16px; padding:20px;">
                <h3 style="margin:0 0 6px; color:#1E5620; font-size:18px;">💡 Agricultural Spraying & Irrigation Advisory</h3>
                <p style="margin:0; color:#4A3525; font-size:14px;">
                    Current weather condition: <b>{weather['description'].title()}</b>. Humidity is <b>{weather['humidity']}%</b>. 
                    {'Avoid foliar spray due to elevated moisture level.' if weather['humidity'] > 75 else 'Favorable condition for crop irrigation and fertilizer application.'}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_icon:
        icon_url = f"https://openweathermap.org/img/wn/{weather['icon']}@2x.png"
        st.image(icon_url, width=100, caption=weather['description'].title())

else:
    st.error("Unable to load live weather data at this moment.")