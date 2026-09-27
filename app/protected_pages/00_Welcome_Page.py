import os
import base64
import streamlit as st
import streamlit.components.v1 as components
from streamlit_geolocation import streamlit_geolocation

from auth.session import get_current_user
from utils.weather_api import get_weather, get_auto_location
from auth.database import get_advisers, create_help_request, get_farmer_help_requests
from utils.llm_client import run_llm
from utils.theme import apply_premium_theme
from utils.i18n import t, language_selector
from utils.live_refresh import live_fragment

apply_premium_theme()


# ==========================================================
# GOVERNMENT SCHEMES DATA & DIALOG MODAL
# ==========================================================

SCHEMES_DATA = [
    {
        "title": "PM-KISAN Direct Income Support",
        "subtitle": "₹6,000 annual financial assistance to farmer families in 3 equal installments",
        "badge": "₹6,000 / year",
        "details": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a Central Sector scheme to provide income support to all landholding farmers' families in the country to supplement their financial needs for procuring various inputs related to agriculture and allied activities.",
        "link": "https://pmkisan.gov.in/",
        "image": "scheme_pmkisan.jpg"
    },
    {
        "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "subtitle": "Comprehensive crop insurance cover against yield losses due to non-preventable risks",
        "badge": "Crop Insurance",
        "details": "PMFBY provides a comprehensive insurance cover against failure of the crop, helping in stabilizing the income of the farmers. Premium rates are just 2% for Kharif crops, 1.5% for Rabi crops and 5% for Annual Commercial / Horticultural crops.",
        "link": "https://pmfby.gov.in/",
        "image": "scheme_pmfby.jpg"
    },
    {
        "title": "Soil Health Card Scheme",
        "subtitle": "Free soil testing and customized NPK nutrient recommendations for your land",
        "badge": "Free Soil Test",
        "details": "Soil Health Card scheme provides information to farmers on nutrient status of their soil along with recommendation on appropriate dosage of nutrients to be applied for improving soil health and its fertility.",
        "link": "https://soilhealth.dac.gov.in/",
        "image": "scheme_soil_health.jpg"
    },
    {
        "title": "PM Krishi Sinchayee Yojana (PMKSY)",
        "subtitle": "Per Drop More Crop - Subsidies up to 80% on micro-irrigation & drip systems",
        "badge": "80% Subsidy",
        "details": "PMKSY aims to expand cultivable area under assured irrigation, improve on-farm water use efficiency to reduce wastage of water, enhance adoption of precision-irrigation and other water saving technologies (Per Drop More Crop).",
        "link": "https://pmksy.gov.in/",
        "image": "scheme_pmksy.jpg"
    },
    {
        "title": "Kisan Credit Card (KCC)",
        "subtitle": "Collateral-free short-term credit up to ₹3 lakhs for seeds, fertilizer & farm expenses",
        "badge": "Up to ₹3 Lakhs",
        "details": "The Kisan Credit Card scheme gives farmers timely access to affordable, collateral-free credit for crop production and other farm needs, at concessional interest rates, repayable after harvest.",
        "link": "https://www.myscheme.gov.in/schemes/kcc",
        "image": "scheme_kcc.jpg"
    }
]

@st.dialog("📜 Government Scheme Details")
def show_scheme_modal(scheme_idx):
    scheme = SCHEMES_DATA[scheme_idx]
    st.markdown(f"### 🏷️ {scheme['title']}")
    st.caption(f"Category: {scheme['badge']}")
    st.info(scheme['subtitle'])
    st.write(scheme['details'])
    st.markdown(f"🔗 **Official Govt Portal:** [{scheme['link']}]({scheme['link']})")
    
    if st.button("Close Modal", type="primary", use_container_width=True):
        st.rerun()


# ==========================================================
# QUICK ACTION DIALOG MODALS
# ==========================================================

@st.dialog("🌱 Soil Health Analysis")
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
# IMAGE ASSETS (embedded as base64 so they always load,
# regardless of how Streamlit is serving static files)
# ==========================================================

ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "assets",
)


_ASSET_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".mp3": "audio/mpeg",
}


@st.cache_data(show_spinner=False)
def _get_asset_data_uri(filename):
    image_path = os.path.join(ASSETS_DIR, filename)
    ext = os.path.splitext(filename)[1].lower()
    mime = _ASSET_MIME_TYPES.get(ext, "application/octet-stream")
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode("ascii")
                return f"data:{mime};base64,{encoded}"
    except Exception:
        pass
    return ""


AMBIENT_AUDIO_PATH = os.path.join(ASSETS_DIR, "farm-ambient.mp3")


def _get_hero_image_data_uri():
    # Prefer the newer dashboard hero photo; fall back to the original
    # welcome_page.png if it isn't present for any reason.
    for filename in ("hero_dashboard.jpg", "welcome_page.png"):
        data_uri = _get_asset_data_uri(filename)
        if data_uri:
            return f"url({data_uri})"
    return ""


_hero_bg_image = _get_hero_image_data_uri()


# ==========================================================
# DASHBOARD CSS STYLING
# ==========================================================

_dashboard_css = """
    <style>
    .stApp { background: #F4F6F0; }
    
    /* Header Bar */
    .dashboard-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border-bottom: 1px solid #e2ece4;
        padding: 12px 24px;
        margin: -1.5rem -1.5rem 1.5rem -1.5rem;
    }
    .header-logo-badge {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .header-logo-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1E5620, #2D7D32);
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 0 4px 14px rgba(30,86,32,0.2);
    }
    .header-user-tag {
        background: #f0f7f1;
        border: 1px solid #cce3d2;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 13px;
        font-weight: 700;
        color: #1E5620;
    }

    /* Hero Section Banner */
    .farm-hero-banner {
        position: relative;
        background: linear-gradient(105deg, rgba(30, 86, 32, 0.92), rgba(45, 125, 65, 0.82), rgba(229, 169, 60, 0.55)), __HERO_BG_IMAGE__;
        background-size: cover;
        background-position: center;
        color: white;
        padding: 32px 36px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 10px 28px rgba(30, 86, 32, 0.16);
    }
    .farm-hero-banner h2 { margin: 0 0 6px; font-size: 28px; font-weight: 800; }
    .farm-hero-banner p { margin: 0 0 12px; color: #e3f4e5; font-size: 15px; }
    .hero-badge {
        background: #E5A93C;
        color: #4A3525;
        font-weight: 800;
        font-size: 12px;
        padding: 6px 14px;
        border-radius: 20px;
        display: inline-block;
    }

    /* Schemes Section */
    .schemes-header {
        text-align: center;
        margin: 28px 0 16px;
    }
    .schemes-header h2 { margin: 0; font-size: 24px; font-weight: 800; color: #1E5620; }
    .schemes-header p { margin: 4px 0 0; font-size: 14px; color: #6D4C41; }
    
    .scheme-card-banner {
        position: relative;
        background-size: cover;
        background-position: center;
        color: #ffffff;
        padding: 30px 36px;
        border-radius: 20px;
        min-height: 170px;
        box-shadow: 0 12px 28px rgba(30, 86, 32, 0.22);
        margin-bottom: 28px;
    }
    .scheme-badge {
        position: absolute;
        top: 24px;
        right: 32px;
        background: #E5A93C;
        color: #3e2c0f;
        font-weight: 800;
        font-size: 13px;
        padding: 6px 14px;
        border-radius: 20px;
    }
    .scheme-card-banner h3 { margin: 0 0 8px; font-size: 26px; font-weight: 800; color: #ffffff; text-shadow: 0 2px 8px rgba(0,0,0,0.35); }
    .scheme-card-banner p { margin: 0 0 18px; font-size: 15px; color: #f3f3f3; max-width: 650px; text-shadow: 0 1px 6px rgba(0,0,0,0.3); }

    /* Action Cards */
    .quick-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    .action-card-btn {
        background: #ffffff;
        border: 1px solid #dce9de;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .action-card-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    .action-icon-wrap {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px;
        font-size: 22px;
        color: white;
    }
    
    .badge-pending { background: #fef3c7; color: #92400e; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: 800; }
    .badge-answered { background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: 800; }
    
    iframe[title="streamlit_geolocation.streamlit_geolocation"] { display: none !important; }

    /* Language dropdown: align it properly within the header row instead
       of the previous unstyled/misaligned default select box. */
    .st-key-header_lang_wrap [data-testid="stSelectbox"] {
        margin-top: 2px;
    }
    .st-key-header_lang_wrap [data-testid="stSelectbox"] > div > div {
        border-radius: 10px;
        border-color: #cce3d2;
        background: #f8fcf8;
        min-height: 40px;
    }

    /* Ambient audio player: fully functional, but visually hidden so it
       doesn't clutter the header (control is the Audio toggle button). */
    .st-key-ambient_audio_box {
        position: absolute;
        width: 1px;
        height: 1px;
        overflow: hidden;
        opacity: 0;
        pointer-events: none;
    }
    </style>
    """

st.markdown(
    _dashboard_css.replace(
        "__HERO_BG_IMAGE__",
        _hero_bg_image if _hero_bg_image else "none",
    ),
    unsafe_allow_html=True,
)

user = get_current_user() or {}
user_id = user.get("id", 1)
farmer_name = user.get("full_name", "Farmer")


# ==========================================================
# TOP HEADER BAR
# ==========================================================

head_left, head_right = st.columns([2, 2])

if "ambient_audio_on" not in st.session_state:
    st.session_state.ambient_audio_on = False

with head_left:
    st.markdown(
        f"""
        <div class="dashboard-header-bar">
            <div class="header-logo-badge">
                <div class="header-logo-icon">🌿</div>
                <div>
                    <h3 style="margin:0; font-size:18px; font-weight:800; color:#1E5620;">{t('welcome', name=farmer_name)}</h3>
                    <div style="font-size:12px; color:#6D4C41; font-weight:500;">{t('dashboard_subtitle')}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with head_right:
    c1, c2, c3 = st.columns([1.5, 1.2, 1.3])
    with c1:
        with st.container(key="header_lang_wrap"):
            language_selector(key="dash_lang_selector")
    with c2:
        audio_label = t("audio_on") if st.session_state.ambient_audio_on else t("audio_off")
        if st.button(audio_label, key="head_audio_btn", use_container_width=True):
            st.session_state.ambient_audio_on = not st.session_state.ambient_audio_on
            st.rerun()
    with c3:
        st.markdown(f'<div class="header-user-tag">👤 {farmer_name}</div>', unsafe_allow_html=True)

if st.session_state.ambient_audio_on and os.path.exists(AMBIENT_AUDIO_PATH):
    with st.container(key="ambient_audio_box"):
        try:
            st.audio(AMBIENT_AUDIO_PATH, format="audio/mp3", autoplay=True, loop=True)
        except TypeError:
            # Older Streamlit versions without the `loop` parameter.
            st.audio(AMBIENT_AUDIO_PATH, format="audio/mp3", autoplay=True)


# ==========================================================
# HERO BANNER SECTION
# ==========================================================

st.markdown(
    f"""
    <div class="farm-hero-banner">
        <h2>{t('hero_title')}</h2>
        <p>{t('hero_sub')}</p>
        <span class="hero-badge">{t('hero_badge')}</span>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# GOVERNMENT SCHEMES FOR FARMERS (CAROUSEL SLIDER)
# ==========================================================

st.markdown(
    f"""
    <div class="schemes-header">
        <h2>{t('schemes_title')}</h2>
        <p>{t('schemes_sub')}</p>
    </div>
    """,
    unsafe_allow_html=True
)

if "scheme_index" not in st.session_state:
    st.session_state.scheme_index = 0

curr_idx = st.session_state.scheme_index
curr_scheme = SCHEMES_DATA[curr_idx]

scheme_col, nav_col1, nav_col2 = st.columns([8, 1, 1])

with scheme_col:
    scheme_img_uri = _get_asset_data_uri(curr_scheme.get("image", ""))
    scheme_bg_style = (
        f"background-image: linear-gradient(120deg, rgba(30,86,32,0.80), rgba(45,125,65,0.55)), url({scheme_img_uri});"
        if scheme_img_uri
        else "background: linear-gradient(110deg, #1E5620, #2D7D32 50%, #E5A93C);"
    )
    st.markdown(
        f"""
        <div class="scheme-card-banner" style="{scheme_bg_style}">
            <span class="scheme-badge">{curr_scheme['badge']}</span>
            <h3>{curr_scheme['title']}</h3>
            <p>{curr_scheme['subtitle']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    b_col1, b_col2 = st.columns([1.5, 2])
    with b_col1:
        if st.button(t("apply_now"), key=f"scheme_apply_{curr_idx}", type="primary", use_container_width=True):
            show_scheme_modal(curr_idx)
    with b_col2:
        if st.button(t("learn_more"), key=f"scheme_learn_{curr_idx}", use_container_width=True):
            show_scheme_modal(curr_idx)

with nav_col1:
    st.write("")
    st.write("")
    st.write("")
    if st.button(t("prev"), key="scheme_prev", use_container_width=True):
        st.session_state.scheme_index = (curr_idx - 1) % len(SCHEMES_DATA)
        st.rerun()

with nav_col2:
    st.write("")
    st.write("")
    st.write("")
    if st.button(t("next"), key="scheme_next", use_container_width=True):
        st.session_state.scheme_index = (curr_idx + 1) % len(SCHEMES_DATA)
        st.rerun()

# Auto-advance the schemes carousel every few seconds, so farmers don't
# have to click "Next" manually. This works by having a tiny injected
# script find and click the real "Next" button on a timer — it does not
# change the Prev/Next buttons themselves, so manual navigation still
# works normally too.
components.html(
    f"""
    <script>
    setTimeout(function() {{
        try {{
            const doc = window.parent.document;
            const buttons = doc.querySelectorAll('button');
            for (const btn of buttons) {{
                if (btn.innerText && btn.innerText.trim() === {t('next')!r}) {{
                    btn.click();
                    break;
                }}
            }}
        }} catch (e) {{}}
    }}, 7000);
    </script>
    """,
    height=0,
)

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================================
# MAIN 2-COLUMN DASHBOARD GRID
# ==========================================================

left_col, right_col = st.columns([2, 1], gap="large")


# ----------------------------------------------------------
# LEFT COLUMN: WEATHER, QUICK ACTIONS, RECENT ACTIVITIES
# ----------------------------------------------------------
with left_col:
    # 1. WEATHER WIDGET
    st.markdown(f"### {t('weather_today')}")
    location = streamlit_geolocation()
    # Same auto-detection the Weather page uses: browser GPS first, then
    # IP-based geolocation, then a last-resort default — instead of always
    # falling back to a hardcoded Bangalore coordinate whenever the browser
    # hasn't granted GPS permission yet (which is what made this widget show
    # Bangalore's weather no matter where the farmer actually is).
    lat, lon, _location_source = get_auto_location(location)

    weather = get_weather(latitude=float(lat), longitude=float(lon))
    if weather.get("success"):
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1E5620 0%, #2D7D32 100%); color:white; border-radius:18px; padding:22px; box-shadow:0 8px 24px rgba(30,86,32,0.15);">
                <div style="font-size:16px; font-weight:700;">📍 {weather['city']}, {weather['country']}</div>
                <div style="font-size:38px; font-weight:850; margin:6px 0;">{weather['temperature']}°C</div>
                <div style="font-size:14px; color:#F5F5DC;">{weather['description'].title()} &nbsp;|&nbsp; 💧 Humidity: {weather['humidity']}% &nbsp;|&nbsp; 🌬 Wind: {weather['wind_speed']} m/s</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. QUICK ACTIONS
    st.markdown(f"### {t('quick_actions')}")
    st.caption(t("quick_actions_sub"))

    q1, q2 = st.columns(2)
    with q1:
        with st.container(border=True):
            st.markdown('<div class="action-icon-wrap bg-gradient-success">📷</div>', unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align:center; margin:0 0 4px;'>{t('scan_crop')}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#666; margin:0 0 12px;'>{t('scan_crop_sub')}</p>", unsafe_allow_html=True)
            if st.button(t("open_scanner"), key="qa_scan", type="primary", use_container_width=True):
                st.session_state["active_page"] = "Disease Detection"
                st.rerun()

        with st.container(border=True):
            st.markdown('<div class="action-icon-wrap bg-gradient-harvest">📈</div>', unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align:center; margin:0 0 4px;'>{t('view_prices')}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#666; margin:0 0 12px;'>{t('view_prices_sub')}</p>", unsafe_allow_html=True)
            if st.button(t("check_rates"), key="qa_rates", use_container_width=True):
                st.session_state["active_page"] = "Market Prices"
                st.rerun()

        with st.container(border=True):
            st.markdown('<div class="action-icon-wrap bg-gradient-earth">☀️</div>', unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align:center; margin:0 0 4px;'>{t('field_advisor')}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#666; margin:0 0 12px;'>{t('field_advisor_sub')}</p>", unsafe_allow_html=True)
            if st.button(t("launch_advisor"), key="qa_field_adv", use_container_width=True):
                st.session_state["active_page"] = "Field Advisor"
                st.rerun()

    with q2:
        with st.container(border=True):
            st.markdown('<div class="action-icon-wrap bg-gradient-earth">🌱</div>', unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align:center; margin:0 0 4px;'>{t('check_soil')}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#666; margin:0 0 12px;'>{t('check_soil_sub')}</p>", unsafe_allow_html=True)
            if st.button(t("analyze_soil"), key="qa_soil", use_container_width=True):
                show_soil_health_modal()

        with st.container(border=True):
            st.markdown('<div class="action-icon-wrap bg-gradient-sky">💬</div>', unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align:center; margin:0 0 4px;'>{t('get_advice')}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#666; margin:0 0 12px;'>{t('get_advice_sub')}</p>", unsafe_allow_html=True)
            if st.button(t("open_ai_advisory"), key="qa_ai_adv", use_container_width=True):
                show_ai_chat_modal()

        with st.container(border=True):
            st.markdown('<div class="action-icon-wrap bg-gradient-success">✉️</div>', unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align:center; margin:0 0 4px;'>{t('ask_expert')}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#666; margin:0 0 12px;'>{t('ask_expert_sub')}</p>", unsafe_allow_html=True)
            if st.button(t("submit_question"), key="qa_expert_btn", use_container_width=True):
                show_ask_expert_modal(user_id)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. RECENT ACTIVITIES
    st.markdown(f"### {t('recent_activities')}")
    st.caption(t("recent_activities_sub"))
    
    with st.container(border=True):
        st.markdown(
            """
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #eee;">
                <div>
                    <strong>📷 Pest scan completed</strong><br>
                    <span style="font-size:12px; color:#666;">Tomato crop - No issues found</span>
                </div>
                <span class="badge-answered">Today</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0;">
                <div>
                    <strong>🌱 Soil health checked</strong><br>
                    <span style="font-size:12px; color:#666;">Field A - pH level optimal</span>
                </div>
                <span class="badge-pending">Yesterday</span>
            </div>
            """,
            unsafe_allow_html=True
        )


# ----------------------------------------------------------
# RIGHT COLUMN: AI ASSISTANT, ALERTS & NOTIFICATIONS
# ----------------------------------------------------------
with right_col:
    # 1. AI ASSISTANT CARD
    with st.container(border=True):
        st.markdown(f"### {t('ai_assistant')}")
        st.caption(t("ai_assistant_sub"))

        if st.button(t("chat_ai"), key="right_chat_btn", type="primary", use_container_width=True):
            show_ai_chat_modal()
            
        st.markdown(
            """
            <div style="background:#f0f7f1; border-left:4px solid #1E5620; border-radius:10px; padding:12px; margin-top:12px; font-size:13px; color:#1E5620;">
                💡 <b>Tip:</b> Ask me about crop rotation, fertilizers, or weather patterns!
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. ALERTS & REMINDERS CARD
    with st.container(border=True):
        st.markdown(f"### {t('alerts_title')}")
        st.markdown(
            """
            <div style="background:#fffbe6; border-left:4px solid #E5A93C; border-radius:10px; padding:12px; margin-bottom:10px; font-size:13px; color:#78350f;">
                <strong>Irrigation Reminder</strong><br>
                Field B needs watering in 2 hours.
            </div>
            <div style="background:#e0f2fe; border-left:4px solid #0284C7; border-radius:10px; padding:12px; font-size:13px; color:#0369a1;">
                <strong>Weather Alert</strong><br>
                Rain expected tomorrow evening.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. NOTIFICATIONS CARD
    with st.container(border=True):
        st.markdown(f"### {t('notifications_title')}")
        st.caption(t("notifications_sub"))

        @live_fragment("5s")
        def _render_notifications():
            # Re-queried fresh on every tick, so an adviser's reply shows
            # up here within a few seconds without reloading the page.
            requests = get_farmer_help_requests(user_id)
            if requests:
                for r in requests[:2]:
                    st.markdown(
                        f"""
                        <div style="background:#f8faf8; border:1px solid #e2ece4; border-radius:10px; padding:10px; margin-bottom:8px; font-size:12px;">
                            <strong>{r['subject']}</strong><br>
                            <span style="color:#666;">Status: {r['status']}</span>
                            {f'<br><span style="color:#1E5620;"><b>Reply:</b> {r["reply"]}</span>' if r['reply'] else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.caption("No new notifications")

        _render_notifications()
