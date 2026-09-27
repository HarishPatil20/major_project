import os
import streamlit as st

from utils.species_mapping import DISEASE_LABELS
from utils.llm_client import run_llm
from utils.theme import apply_premium_theme

apply_premium_theme()


# ==========================================================
# PAGE STYLE
# ==========================================================

st.markdown(
    """
    <style>
    .species-hero {
        background: linear-gradient(135deg, #1E5620 0%, #2D7D32 60%, #E5A93C 100%);
        color: white;
        padding: 30px clamp(20px, 4vw, 40px);
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 12px 30px rgba(30, 86, 32, 0.2);
    }
    .species-hero h1 { margin: 0; font-size: clamp(24px, 4vw, 36px); font-weight: 800; }
    .species-hero p { margin: 8px 0 0; color: #F5F5DC; font-size: 15px; }

    .st-key-species_picker {
        background: #ffffff;
        border: 1px solid #E2E8DC;
        border-radius: 20px;
        padding: clamp(14px, 2.2vw, 24px);
        margin-bottom: 20px;
        box-shadow: 0 6px 18px rgba(30, 86, 32, 0.06);
    }
    .species-picker-title {
        font-size: 15px;
        font-weight: 700;
        color: #4B5A45;
        margin-bottom: 12px;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }

    .st-key-species_detail {
        background: linear-gradient(160deg, #ffffff 0%, #F7FAF3 100%);
        border: 1px solid #DCEBD3;
        border-left: 5px solid #2D7D32;
        border-radius: 20px;
        padding: clamp(16px, 2.6vw, 28px);
        margin-bottom: 20px;
        box-shadow: 0 10px 26px rgba(30, 86, 32, 0.08);
    }
    .species-detail-title {
        font-size: 22px;
        font-weight: 800;
        color: #1E5620;
        margin-bottom: 4px;
    }
    .species-detail-subtitle {
        font-size: 13px;
        color: #64748B;
        margin-bottom: 14px;
    }

    .disease-chip {
        display: inline-block;
        padding: 5px 14px;
        margin: 3px 6px 3px 0;
        border-radius: 999px;
        background: rgba(45, 125, 50, 0.10);
        border: 1px solid rgba(45, 125, 50, 0.25);
        color: #1E5620;
        font-size: 12.5px;
        font-weight: 700;
    }

    .ai-guide-title {
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
        font-size: 18px;
        font-weight: 800;
        margin: 4px 0 10px;
        display: inline-block;
    }
    </style>
    <div class="species-hero">
        <h1>🌿 Supported Species for Detection &amp; Classification</h1>
        <p>Pick a crop to preview a real leaf sample and get an AI-generated crop guide.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Only the crops the Disease Detection page can actually run a trained
# model on (Arecanut, Rice, Corn). This list used to include 14 extra
# crops with no trained model behind them, which meant a farmer could
# read about e.g. Tomato or Potato here and then find them unavailable
# on the Detection page - and even for Rice, the diseases shown were
# from an old dataset that no longer matches the real model's output.
# Trimmed to keep this page and the Detection page in sync.
species_data = [
    ("🌴 Arecanut", "arecanut"),
    ("🌾 Rice", "rice"),
    ("🌽 Corn (Maize)", "corn"),
]

# -------------------------------------------------
# Image Folder
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.abspath(
    os.path.join(BASE_DIR, "..", "species_images")
)


def get_image_path(key):
    if not os.path.exists(IMAGE_FOLDER):
        return None

    for file in os.listdir(IMAGE_FOLDER):
        filename, extension = os.path.splitext(file)

        if filename.lower() == key.lower():
            return os.path.join(IMAGE_FOLDER, file)

    return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_species_info(label: str, diseases: tuple) -> str:
    """Cached AI crop guide for one species.

    Without this cache, run_llm() (a local Ollama call) re-generated the
    same text on EVERY page rerun for as long as a species stayed
    selected - including reruns triggered by clicking something else on
    the page entirely. Caching per (label, diseases) means the local
    model only runs again when the user actually picks a different
    species, exactly like the pattern already used for weather/location
    lookups elsewhere in the app. Does not change the prompt, the model,
    or the content generated - only how often it's regenerated.
    """

    prompt = f"""
You are an Agriculture Expert.

Give information in simple English.

Crop:
{label}

Include:

1. Crop Introduction
2. Uses
3. Growing Season
4. Suitable Soil
5. Water Requirement
6. Common Diseases

Diseases:
{', '.join(diseases)}

For each disease provide:

• Cause

• Symptoms

• Prevention

• Treatment

Use headings and bullet points.
"""

    return run_llm(prompt)


if "selected_species" not in st.session_state:
    st.session_state.selected_species = None


with st.container(key="species_picker"):

    st.markdown(
        '<div class="species-picker-title">🔍 Choose a crop</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4)

    for i, (label, key) in enumerate(species_data):
        with cols[i % 4]:
            is_selected = st.session_state.selected_species == key
            if st.button(
                label,
                use_container_width=True,
                type="primary" if is_selected else "secondary",
                key=f"species_btn_{key}",
            ):
                st.session_state.selected_species = key


if st.session_state.selected_species:

    key = st.session_state.selected_species

    label = next(lbl for lbl, k in species_data if k == key)

    diseases = DISEASE_LABELS.get(key, [])

    image_path = get_image_path(key)

    with st.container(key="species_detail"):

        header_columns = st.columns([4, 1])

        with header_columns[0]:
            st.markdown(
                f'<div class="species-detail-title">{label}</div>'
                f'<div class="species-detail-subtitle">AI-generated crop guide</div>',
                unsafe_allow_html=True,
            )

        with header_columns[1]:
            if st.button("✖ Clear", use_container_width=True):
                st.session_state.selected_species = None
                st.rerun()

        col1, col2 = st.columns([1, 2])

        with col1:

            if image_path:
                st.image(
                    image_path,
                    caption=label,
                    use_container_width=True
                )
            else:
                st.warning("🖼️ No sample image available for this crop yet.")

            if diseases:
                st.markdown(
                    "".join(
                        f'<span class="disease-chip">🦠 {d}</span>'
                        for d in diseases
                    ),
                    unsafe_allow_html=True,
                )

        with col2:

            st.markdown(
                '<div class="ai-guide-title">🤖 AI-Generated Crop Guide</div>',
                unsafe_allow_html=True,
            )

            with st.spinner("Generating AI information..."):
                response = get_species_info(label, tuple(diseases))

            st.markdown(response)

else:

    st.info("👆 Choose a crop above to view its information.")
