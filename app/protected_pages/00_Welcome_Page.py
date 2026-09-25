import os

import streamlit as st
from streamlit_geolocation import streamlit_geolocation

from auth.session import get_current_user
from utils.weather_api import get_weather


st.markdown(
    """
    <style>
    .farmer-dashboard { color: #16321f; }
    .dashboard-topline { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 14px; }
    .dashboard-kicker { color: #247044; font-size: 12px; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; }
    .dashboard-date { color: #78907d; font-size: 12px; }
    .farm-hero { background: linear-gradient(105deg, rgba(18, 78, 43, .94), rgba(45, 125, 65, .78)), url('/assets/welcome_page.png'); background-size: cover; background-position: center; color: white; padding: 25px 28px; border-radius: 18px; min-height: 150px; box-shadow: 0 12px 26px rgba(21, 87, 43, .16); }
    .farm-hero h1 { margin: 0; font-size: clamp(25px, 3vw, 36px); }
    .farm-hero p { margin: 8px 0 0; color: #e4f7e7; font-size: 14px; }
    .section-label { color: #183d24; font-size: 18px; font-weight: 800; margin: 22px 0 10px; }
    .scheme-banner { background: linear-gradient(110deg, #d8c17c, #f2df9e 52%, #bb8d3a); color: #3e2c0f; padding: 20px 24px; border-radius: 16px; min-height: 118px; }
    .scheme-banner h2 { margin: 0; font-size: 22px; }
    .scheme-banner p { margin: 8px 0 0; font-size: 13px; }
    .dashboard-card { background: #ffffff; border: 1px solid #d8e7db; border-radius: 14px; padding: 16px; min-height: 105px; box-shadow: 0 6px 18px rgba(23, 66, 31, .045); }
    .dashboard-card h3 { margin: 0 0 5px; color: #1e4729; font-size: 16px; }
    .dashboard-card p { margin: 0; color: #708074; font-size: 12px; }
    .weather-panel { background: linear-gradient(135deg, #146b2d, #1f7a34); color: white; border-radius: 16px; padding: 18px; min-height: 245px; }
    .weather-panel h2 { margin: 0; font-size: 18px; }
    .weather-temp { font-size: 38px; font-weight: 850; margin-top: 18px; }
    .weather-meta { color: #d7f2d9; font-size: 12px; }
    .metric-chip { background: rgba(255,255,255,.13); border-radius: 8px; padding: 8px; color: #effff0; font-size: 11px; }
    .alert-card { background: #fff8df; border: 1px solid #efd994; border-radius: 12px; padding: 13px; margin-bottom: 10px; color: #725716; font-size: 12px; }
    .activity-row { background: #f1f7f2; border-radius: 10px; padding: 10px 12px; margin: 7px 0; color: #4d6252; font-size: 12px; }
    @media (max-width: 700px) {
        .farm-hero { padding: 22px 20px; border-radius: 15px; }
        .scheme-banner { padding: 18px; }
        .dashboard-topline { display: block; }
        .dashboard-date { margin-top: 4px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

user = get_current_user() or {}
farmer_name = user.get("full_name", "Farmer")

st.markdown(
    f"""
    <div class="dashboard-topline">
        <div class="dashboard-kicker">🌾 Smart Crop Advisory</div>
        <div class="dashboard-date">Welcome back, {farmer_name}</div>
    </div>
    <div class="farm-hero">
        <h1>Smart farming today</h1>
        <p>AI-powered insights to help you make better crop decisions.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">Government schemes for farmers</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="scheme-banner">
        <h2>PM-KISAN Direct Income Support</h2>
        <p>Explore official farmer schemes and available agricultural support through the Government Schemes section.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

weather_col, assistant_col = st.columns([2, 1], gap="medium")
with weather_col:
    st.markdown('<div class="section-label">Weather today</div>', unsafe_allow_html=True)
    location = streamlit_geolocation()
    latitude = location.get("latitude") if location else None
    longitude = location.get("longitude") if location else None
    if latitude is not None and longitude is not None:
        weather = get_weather(latitude=float(latitude), longitude=float(longitude))
    else:
        weather = {"success": False}

    if weather.get("success"):
        st.markdown(
            f"""
            <div class="weather-panel">
                <h2>☁ Weather near {weather['city']}, {weather['country']}</h2>
                <div class="weather-temp">{weather['temperature']}°C</div>
                <div class="weather-meta">{weather['description'].title()}</div>
                <div style="height:16px"></div>
                <div class="metric-chip">💧 Humidity {weather['humidity']}%</div>
                <div style="height:7px"></div>
                <div class="metric-chip">🌬 Wind {weather['wind_speed']} m/s</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="weather-panel"><h2>☀ Weather today</h2><div class="weather-meta" style="margin-top:18px">Allow location access to view your live local weather.</div></div>',
            unsafe_allow_html=True,
        )

with assistant_col:
    st.markdown('<div class="section-label">AI assistant</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="dashboard-card">
            <h3>🤖 Get instant crop guidance</h3>
            <p>Ask about crop rotation, fertilizers, pests, or weather-based planning.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Chat with AI", key="dashboard_chat", use_container_width=True, type="primary"):
        st.session_state["active_page"] = "Crop Assistant"
        st.rerun()

st.markdown('<div class="section-label">Alerts and reminders</div>', unsafe_allow_html=True)
alert_col, notification_col = st.columns(2, gap="medium")
with alert_col:
    st.markdown('<div class="alert-card">⏱ <b>Irrigation reminder</b><br>Check soil moisture before the next watering.</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-card" style="background:#e5f5fb;border-color:#b9dfed;color:#255b70">☁ <b>Weather alert</b><br>Use live weather before spraying or irrigating.</div>', unsafe_allow_html=True)
with notification_col:
    st.markdown('<div class="dashboard-card"><h3>🔔 Notifications</h3><p>Updates from your crop activities.</p><br><p>No new notifications.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-label">Quick actions</div>', unsafe_allow_html=True)
quick_actions = [
    ("🌿", "Scan Crop", "Detect crop disease", "Disease Detection"),
    ("🌱", "Crop Guide", "Explore supported crops", "Supported Species"),
    ("💰", "View Prices", "Latest mandi market rates", "Market Prices"),
    ("💬", "Ask Adviser", "Get expert recommendations", "Ask an Adviser"),
    ("🧑‍🌾", "Field Adviser", "Find help for your crop", "Ask an Adviser"),
    ("🤖", "Ask Expert", "Ask the AI assistant", "Crop Assistant"),
]
quick_columns = st.columns(3)
for index, (icon, title, description, page) in enumerate(quick_actions):
    with quick_columns[index % 3]:
        st.markdown(f'<div class="dashboard-card"><h3>{icon} {title}</h3><p>{description}</p></div>', unsafe_allow_html=True)
        if st.button(f"Open {title}", key=f"dashboard_action_{index}", use_container_width=True):
            st.session_state["active_page"] = page
            st.rerun()

st.markdown('<div class="section-label">Recent activities</div>', unsafe_allow_html=True)
st.markdown('<div class="activity-row">✅ <b>Crop tools ready</b><br>Upload a clear leaf image to begin detection.</div>', unsafe_allow_html=True)
st.markdown('<div class="activity-row">📊 <b>Market intelligence available</b><br>Compare official mandi prices by crop and location.</div>', unsafe_allow_html=True)
