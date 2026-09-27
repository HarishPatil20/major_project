import streamlit as st

from auth.session import get_current_user
from utils.llm_client import run_llm
from utils.theme import apply_premium_theme


apply_premium_theme()

st.markdown(
    """
    <style>
    .stApp { background: #f4f6f0; }
    .advisor-hero {
        background: linear-gradient(135deg, #1E5620 0%, #2D7D32 55%, #4A3525 100%);
        color: white;
        padding: 30px clamp(20px, 4vw, 42px);
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 14px 32px rgba(30, 86, 32, 0.2);
    }
    .advisor-hero h1 { margin: 0; font-size: clamp(26px, 4vw, 40px); font-weight: 800; }
    .advisor-hero p { margin: 8px 0 0; color: #F5F5DC; font-size: 15px; }

    /* These target real st.container(key=...) wrapper elements (a stable
       ".st-key-<key>" class Streamlit adds to the actual DOM parent of
       that container's contents) instead of manual <div> tags split
       across separate st.markdown() calls — each st.markdown() call is
       parsed independently, so an unclosed tag there never really wraps
       later widgets; it only produced an empty, isolated styled box
       (the stray box seen above "Your Field Advisory"). */
    .st-key-advisor_form_card {
        background: #ffffff;
        border: 1px solid #dce9de;
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 22px rgba(30, 86, 32, 0.06);
    }
    .advisor-form-title {
        color: #1E5620;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .advisor-form-sub {
        color: #6D4C41;
        font-size: 13px;
        margin-bottom: 16px;
    }
    .st-key-advisor_result_card {
        background: #ffffff;
        border: 1px solid #dce9de;
        border-left: 5px solid #1E5620;
        border-radius: 16px;
        padding: 22px;
        margin-top: 8px;
        box-shadow: 0 8px 22px rgba(30, 86, 32, 0.07);
    }
    .advisor-result-title {
        color: #1E5620;
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    </style>
    <div class="advisor-hero">
        <h1>🧑‍🌾 Field Advisor</h1>
        <p>Tell us about your soil and field conditions — get instant AI-generated crop and fertilizer guidance.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "field_advisor_result" not in st.session_state:
    st.session_state.field_advisor_result = None

user = get_current_user() or {}
farmer_location_default = user.get("location", "") if isinstance(user, dict) else ""

with st.container(key="advisor_form_card"):
    st.markdown('<div class="advisor-form-title">🧪 Field & Soil Details</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="advisor-form-sub">Fill in what you know — the more detail, the more tailored the advice.</div>',
        unsafe_allow_html=True,
    )

    with st.form("field_advisor_form"):
        c1, c2 = st.columns(2)
        with c1:
            soil_type = st.selectbox(
                "🌱 Soil Type",
                ["Loamy Soil", "Clay Soil", "Sandy Soil", "Black Cotton Soil", "Red Soil", "Alluvial Soil"],
            )
            water_source = st.selectbox(
                "💧 Water Source",
                ["Borewell", "Canal Irrigation", "Rain-fed", "River / Stream", "Drip Irrigation", "Tank / Pond"],
            )
        with c2:
            soil_ph = st.slider("⚗️ Soil pH Level", 4.0, 9.0, 6.5, step=0.1)
            location = st.text_input(
                "📍 Location / District",
                value=farmer_location_default,
                placeholder="e.g. Mangaluru, Karnataka",
            )

        current_crop = st.text_input(
            "🌾 Crop You're Considering (optional)",
            placeholder="e.g. Arecanut, Rice, Corn — leave blank for open recommendations",
        )

        submitted = st.form_submit_button(
            "Get AI Field Advisory →", type="primary", use_container_width=True
        )

    if submitted:
        prompt = f"""
You are an experienced agricultural field advisor helping a farmer in India.

Field conditions:
- Soil type: {soil_type}
- Soil pH: {soil_ph}
- Water source: {water_source}
- Location: {location or "Not specified"}
- Crop under consideration: {current_crop or "Open — suggest the best options"}

Give practical, concise advice in simple English with clear bullet points covering:
1. Best-suited crops for this soil and water combination
2. Suggested fertilizer / nutrient plan (N-P-K guidance)
3. Irrigation frequency advice based on the water source
4. Any soil health precautions given the pH level

Keep it actionable and farmer-friendly. Use headings and bullet points.
"""
        with st.spinner("Analyzing field conditions..."):
            advice = run_llm(prompt)
        st.session_state.field_advisor_result = advice

if st.session_state.field_advisor_result:
    with st.container(key="advisor_result_card"):
        st.markdown('<div class="advisor-result-title">📋 Your Field Advisory</div>', unsafe_allow_html=True)
        st.markdown(st.session_state.field_advisor_result)
