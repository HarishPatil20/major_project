import os
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

from auth.session import get_current_user
from utils.weather_api import get_weather
from auth.database import get_advisers, create_help_request, get_farmer_help_requests
from utils.llm_client import run_llm


# ==========================================================
# DIALOG MODALS FOR QUICK ACTIONS
# ==========================================================

@st.dialog("🌱 Soil Health Advisory")
def show_soil_health_modal():
    st.markdown("### 🧪 Soil Testing & Health Recommendations")
    st.write("Analyze soil quality, pH levels, and get tailored NPK fertilizer guidelines.")
    
    col1, col2 = st.columns(2)
    with col1:
        soil_type = st.selectbox("Soil Type", ["Loamy Soil", "Clay Soil", "Sandy Soil", "Black Cotton Soil", "Red Soil"])
        crop_target = st.selectbox("Target Crop", ["Paddy (Rice)", "Arecanut", "Maize (Corn)", "Tomato", "Cotton"])
    with col2:
        ph_val = st.slider("Soil pH Level", 4.0, 9.0, 6.5)
        moisture = st.select_slider("Moisture Level", options=["Low", "Optimal", "High", "Waterlogged"])
    
    if st.button("Generate Fertilizer Plan →", type="primary", use_container_width=True):
        st.success(f"✅ Recommendations for **{crop_target}** on **{soil_type}** (pH {ph_val}):")
        st.markdown(
            f"""
            - **Nitrogen (N)**: 120 kg/ha (apply in 3 split doses)
            - **Phosphorus (P)**: 60 kg/ha (basal application)
            - **Potassium (K)**: 40 kg/ha (apply at flowering stage)
            - **Organic Matter**: Add 5 tons/ha of FYM (Farm Yard Manure) to balance soil pH.
            """
        )

@st.dialog("🤖 AI Crop Advisory Chat")
def show_ai_chat_modal():
    st.markdown("### 🤖 Instant AI Assistant")
    st.caption("Ask questions about pests, crop rot, fertilizer doses, or weather planning.")
    
    if "modal_messages" not in st.session_state:
        st.session_state.modal_messages = []
        
    for msg in st.session_state.modal_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    prompt = st.chat_input("Ask AI adviser...")
    if prompt:
        st.session_state.modal_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("AI response generating..."):
                resp = run_llm(prompt)
                st.markdown(resp)
        st.session_state.modal_messages.append({"role": "assistant", "content": resp})

@st.dialog("🧑‍🌾 Connect with Field Adviser")
def show_field_advisor_modal():
    st.markdown("### 🧑‍🌾 Registered Agricultural Field Advisers")
    advisers = get_advisers()
    if advisers:
        for adv in advisers:
            st.markdown(
                f"""
                <div style="background:#f4f9f5; border:1px solid #cce5d0; border-radius:12px; padding:14px; margin-bottom:10px;">
                    <div style="font-weight:800; color:#1E5620; font-size:16px;">{adv['full_name']}</div>
                    <div style="color:#E5A93C; font-weight:700; font-size:13px;">Specialization: {adv['specialization']}</div>
                    <div style="color:#4A3525; font-size:13px; margin-top:4px;">📍 {adv['location']} &nbsp;|&nbsp; 📞 {adv['phone']}</div>
                    <div style="font-size:12px; color:#555; margin-top:4px;">Crops: {adv['crops']} | Diseases: {adv['diseases']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No field advisers are currently registered in your area.")

@st.dialog("💬 Ask Expert Question")
def show_ask_expert_modal(user_id):
    st.markdown("### 💬 Submit Question to Expert Team")
    st.write("Describe your farming issue. Experts will review and respond to your query.")
    
    subject = st.text_input("Query Subject", placeholder="e.g., Brown spots on paddy leaves")
    message = st.text_area("Detailed Question", placeholder="Describe crop symptoms, location, and soil conditions...", height=120)
    
    if st.button("Submit Query →", type="primary", use_container_width=True):
        if subject.strip() and message.strip():
            create_help_request(user_id, subject, message)
            st.success("🎉 Query submitted! You can view response status under 'Ask an Adviser'.")
            st.rerun()
        else:
            st.error("Please fill in both subject and detailed question.")


# ==========================================================
# DASHBOARD STYLING
# ==========================================================

st.markdown(
    """
    <style>
    .farmer-dashboard { color: #16321f; }
    
    /* Header Bar Styling */
    .dashboard-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border: 1px solid #d8e7db;
        border-radius: 16px;
        padding: 12px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(30, 86, 32, 0.05);
    }
    .header-logo-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 800;
        font-size: 18px;
        color: #1E5620;
    }
    .header-logo-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, #1E5620, #2D7D32);
        color: #E5A93C;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .header-actions {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .header-pill {
        background: #f0f7f1;
        border: 1px solid #cce3d2;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 600;
        color: #1E5620;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .bell-badge {
        position: relative;
        background: #fef3c7;
        color: #b45309;
        border: 1px solid #fde68a;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 700;
    }

    /* Hero Banner */
    .farm-hero {
        background: linear-gradient(135deg, rgba(30, 86, 32, 0.95), rgba(45, 125, 65, 0.85)), url('/assets/welcome_page.png');
        background-size: cover;
        background-position: center;
        color: white;
        padding: 28px 32px;
        border-radius: 22px;
        margin-bottom: 20px;
        box-shadow: 0 12px 30px rgba(30, 86, 32, 0.18);
    }
    .farm-hero h1 { margin: 0; font-size: clamp(26px, 3.5vw, 38px); font-weight: 800; }
    .farm-hero p { margin: 8px 0 0; color: #F5F5DC; font-size: 15px; }
    
    /* Alert Banner Badge */
    .weather-alert-banner {
        background: linear-gradient(90deg, #fffbe6, #fff3c4);
        border: 1px solid #fce895;
        border-left: 6px solid #E5A93C;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 22px;
        color: #78350f;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .weather-alert-badge {
        background: #E5A93C;
        color: #4A3525;
        font-weight: 800;
        font-size: 11px;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .section-label { color: #1E5620; font-size: 20px; font-weight: 800; margin: 24px 0 12px; display: flex; align-items: center; gap: 8px; }

    /* Quick Action Gradient Icon Cards */
    .quick-card {
        border-radius: 18px;
        padding: 20px;
        color: white;
        min-height: 140px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 14px;
    }
    .quick-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.14);
    }
    .quick-card-icon {
        font-size: 32px;
        margin-bottom: 10px;
    }
    .quick-card h3 {
        margin: 0 0 4px;
        font-size: 18px;
        font-weight: 800;
        color: white;
    }
    .quick-card p {
        margin: 0;
        font-size: 12px;
        opacity: 0.92;
    }

    /* Status Badges */
    .badge-pending {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fcd34d;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
    }
    .badge-answered {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #86efac;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
    }

    /* Recent Activities timeline */
    .timeline-item {
        background: #ffffff;
        border: 1px solid #e2ece4;
        border-left: 4px solid #1E5620;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 13px;
        color: #334155;
    }

    @media (max-width: 700px) {
        .dashboard-header-bar { flex-direction: column; align-items: flex-start; gap: 10px; }
        .farm-hero { padding: 22px 20px; border-radius: 16px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

user = get_current_user() or {}
user_id = user.get("id", 1)
farmer_name = user.get("full_name", "Farmer")


# ==========================================================
# HEADER BAR WITH LOGO, LANGUAGE, AUDIO & NOTIFICATION BELL
# ==========================================================

head_left, head_right = st.columns([2, 2])

with head_left:
    st.markdown(
        f"""
        <div class="dashboard-header-bar">
            <div class="header-logo-badge">
                <div class="header-logo-icon">🌾</div>
                <div>
                    <div>Smart Crop Advisory</div>
                    <div style="font-size:11px; font-weight:600; color:#6D4C41;">Welcome back, {farmer_name}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with head_right:
    c1, c2, c3 = st.columns([1.5, 1.2, 1.2])
    with c1:
        lang = st.selectbox("🌐 Language", ["English", "Kannada (ಕನ್ನಡ)", "Hindi (हिंदी)"], label_visibility="collapsed")
    with c2:
        audio_on = st.toggle("🔊 Audio", value=True)
    with c3:
        st.markdown('<div class="bell-badge">🔔 Notifications (2)</div>', unsafe_allow_html=True)


# ==========================================================
# HERO BANNER & WEATHER ALERT BADGE
# ==========================================================

st.markdown(
    f"""
    <div class="farm-hero">
        <h1>Smart Farming & Crop Intelligence</h1>
        <p>AI-powered crop diagnostics, soil health recommendations, and live mandi market insights.</p>
    </div>
    <div class="weather-alert-banner">
        <div>
            <span class="weather-alert-badge">⚠️ Weather Alert</span>
            <strong style="margin-left:8px;">Localized Advisory:</strong> Light rain expected tomorrow evening in your area. Delay pesticide spraying.
        </div>
        <div style="font-weight:700; font-size:12px;">Live Updates ☁</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# 6 QUICK ACTION GRADIENT ICON CARDS
# ==========================================================

st.markdown('<div class="section-label">🚀 Quick Action Hub</div>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown(
        """
        <div class="quick-card bg-gradient-primary">
            <div class="quick-card-icon">🌿</div>
            <h3>Crop Scanner</h3>
            <p>Upload crop leaf photos for instant AI disease detection & remedy treatment.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Crop Scanner →", key="act_scanner", type="primary", use_container_width=True):
        st.session_state["active_page"] = "Disease Detection"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="quick-card bg-gradient-sky">
            <div class="quick-card-icon">🤖</div>
            <h3>AI Chat Modal</h3>
            <p>Ask instant questions about crop health, pests, or farming best practices.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Launch AI Chat Modal 💬", key="act_ai_modal", use_container_width=True):
        show_ai_chat_modal()

with col_b:
    st.markdown(
        """
        <div class="quick-card bg-gradient-earth">
            <div class="quick-card-icon">🌱</div>
            <h3>Soil Health</h3>
            <p>Soil testing guidelines, NPK fertilizer dosages, and pH management.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Open Soil Health Modal 🧪", key="act_soil_modal", use_container_width=True):
        show_soil_health_modal()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="quick-card bg-gradient-success">
            <div class="quick-card-icon">🧑‍🌾</div>
            <h3>Field Advisor Modal</h3>
            <p>Connect with local agricultural extension officers & crop specialists.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("View Field Advisers 🧑‍🌾", key="act_advisor_modal", use_container_width=True):
        show_field_advisor_modal()

with col_c:
    st.markdown(
        """
        <div class="quick-card bg-gradient-harvest">
            <div class="quick-card-icon">💰</div>
            <h3>Market Prices</h3>
            <p>Check official Mandi commodity prices, trend analysis, and rate alerts.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("View Market Prices →", key="act_market", use_container_width=True):
        st.session_state["active_page"] = "Market Prices"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="quick-card bg-gradient-primary">
            <div class="quick-card-icon">💬</div>
            <h3>Ask Expert Modal</h3>
            <p>Submit crop issues to agricultural experts and track response status.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Ask Expert Question 📩", key="act_expert_modal", use_container_width=True):
        show_ask_expert_modal(user_id)


# ==========================================================
# WEATHER & LIVE ACTIVITY SECTION
# ==========================================================

weather_col, activity_col = st.columns([2, 1], gap="medium")

with weather_col:
    st.markdown('<div class="section-label">🌤 Local Weather Forecast</div>', unsafe_allow_html=True)
    location = streamlit_geolocation()
    lat = location.get("latitude") if location else None
    lon = location.get("longitude") if location else None
    
    if lat is not None and lon is not None:
        weather = get_weather(latitude=float(lat), longitude=float(lon))
    else:
        weather = {"success": False}

    if weather.get("success"):
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1E5620, #2D7D32); color:white; border-radius:18px; padding:22px; box-shadow:0 8px 24px rgba(30,86,32,0.15);">
                <div style="font-size:18px; font-weight:700;">📍 Weather near {weather['city']}, {weather['country']}</div>
                <div style="font-size:42px; font-weight:800; margin:10px 0;">{weather['temperature']}°C</div>
                <div style="font-size:14px; color:#F5F5DC;">{weather['description'].title()} &nbsp;|&nbsp; 💧 Humidity: {weather['humidity']}% &nbsp;|&nbsp; 🌬 Wind: {weather['wind_speed']} m/s</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #1E5620, #2D7D32); color:white; border-radius:18px; padding:22px;">
                <div style="font-size:18px; font-weight:700;">☀️ Local Weather Forecast</div>
                <div style="font-size:14px; margin-top:8px; color:#F5F5DC;">Allow location access in your browser to load live meteorological data.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

with activity_col:
    st.markdown('<div class="section-label">📢 Notifications</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background:#ffffff; border:1px solid #d8e7db; border-radius:16px; padding:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; font-size:13px;">Adviser Reply</span>
                <span class="badge-answered">Answered</span>
            </div>
            <div style="font-size:12px; color:#555;">Expert replied to your query on Paddy Leaf Blight treatment.</div>
            <hr style="margin:10px 0; border:0; border-top:1px solid #eee;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; font-size:13px;">Market Update</span>
                <span class="badge-pending">New Rate</span>
            </div>
            <div style="font-size:12px; color:#555;">Arecanut mandi prices rose +4.2% in Shimoga mandi.</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# RECENT ACTIVITIES TIMELINE & MY QUERIES PANEL
# ==========================================================

st.markdown('<div class="section-label">📋 Recent Activities & Answered Queries</div>', unsafe_allow_html=True)

requests = get_farmer_help_requests(user_id)

if requests:
    for req in requests[:3]:
        badge_cls = "badge-answered" if req["status"] in ["Replied", "Answered"] else "badge-pending"
        st.markdown(
            f"""
            <div class="timeline-item">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <strong style="color:#1E5620; font-size:14px;">{req['subject']}</strong>
                    <span class="{badge_cls}">{req['status']}</span>
                </div>
                <div style="font-size:12px; color:#666;">{req['message']}</div>
                {f'<div style="background:#f0f7f1; border-left:3px solid #1E5620; padding:8px 12px; margin-top:8px; border-radius:6px; color:#1E5620;"><b>Admin Reply:</b> {req["reply"]}</div>' if req.get("reply") else ''}
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.markdown('<div class="timeline-item">✅ <b>Crop Intelligent Assistant Active:</b> All AI models loaded. Upload crop images for immediate classification.</div>', unsafe_allow_html=True)
    st.markdown('<div class="timeline-item">📊 <b>Market Intelligence:</b> Daily mandi commodity prices synced from official government sources.</div>', unsafe_allow_html=True)
