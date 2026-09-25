import os
import streamlit as st

from utils.species_mapping import DISEASE_LABELS
from utils.llm_client import run_llm

st.set_page_config(
    page_title="Supported Species",
    page_icon="🌿",
    layout="wide"
)

st.title("🌿 Supported Species for Detection & Classification")
st.write(
    "Click any species button to preview a real leaf sample and view AI-generated crop information."
)

st.markdown("---")

species_data = [
    ("🍎 Apple", "apple"),
    ("🫐 Blueberry", "blueberry"),
    ("🌿 Cassava", "cassava"),
    ("🍒 Cherry", "cherry"),
    ("🌽 Corn (Maize)", "corn"),
    ("🍇 Grape", "grape"),
    ("🍊 Orange", "orange"),
    ("🍑 Peach", "peach"),
    ("🫑 Pepper", "pepperbell"),
    ("🥔 Potato", "potato"),
    ("🍓 Raspberry", "raspberry"),
    ("🌾 Rice", "rice"),
    ("🌱 Soybean", "soybean"),
    ("🎃 Squash", "squash"),
    ("🍓 Strawberry", "strawberry"),
    ("🍅 Tomato", "tomato"),
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


if "selected_species" not in st.session_state:
    st.session_state.selected_species = None

cols = st.columns(4)

for i, (label, key) in enumerate(species_data):
    with cols[i % 4]:
        if st.button(label, use_container_width=True):
            st.session_state.selected_species = key

st.markdown("---")

if st.session_state.selected_species:

    key = st.session_state.selected_species

    label = next(lbl for lbl, k in species_data if k == key)

    diseases = DISEASE_LABELS.get(key, [])

    image_path = get_image_path(key)

    col1, col2 = st.columns([1, 2])

    with col1:

        if image_path:
            st.image(
                image_path,
                caption=label,
                use_container_width=True
            )
        else:
            st.error("Image not found")
            st.write("Image Folder:", IMAGE_FOLDER)
            st.write("Selected Key:", key)

    with col2:

        st.subheader(label)

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

        with st.spinner("Generating AI information..."):
            response = run_llm(prompt)

        st.markdown(response)

else:

    st.info("👆 Click any crop button above to view information.")