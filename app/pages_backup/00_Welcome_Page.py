import streamlit as st
import os

# ------------------------------------
# PAGE CONFIG
# ------------------------------------
st.set_page_config(
    page_title="Welcome",
    page_icon="🌿",
    layout="wide"
)

# ------------------------------------
# IMAGE LOAD
# ------------------------------------
BASE_DIR = os.path.dirname(__file__)

IMAGE_PATH = os.path.join(
    BASE_DIR,
    "..",
    "assets",
    "welcome_page.png"
)

# ------------------------------------
# TITLE
# ------------------------------------
st.title("🌿An Intelligent Crop Disease Detection System Using Computer Vision and Deep Learning")

# ------------------------------------
# SHOW IMAGE
# ------------------------------------
if os.path.exists(IMAGE_PATH):
    st.image(
        IMAGE_PATH,
        caption="CropDoctor AI - Smart Agriculture",
        use_container_width=True
    )
else:
    st.error(f"❌ Image not found:\n{IMAGE_PATH}")

st.markdown("---")

# ------------------------------------
# INTRODUCTION
# ------------------------------------
st.markdown("""
## 🌱 Welcome to CropDoctor AI

CropDoctor AI is an intelligent agriculture platform powered by **Computer Vision**, **Deep Learning**, and **Artificial Intelligence**.

It helps farmers, students, researchers, and gardeners identify plant species, detect diseases, and improve crop health using AI.
""")

# ------------------------------------
# FEATURES
# ------------------------------------
st.subheader("🚀 Features")

st.markdown("""
- 📸 Upload a plant leaf image
- 🌿 Identify crop species
- 🦠 Detect plant diseases
- 📊 View prediction confidence
- 🔥 Grad-CAM visualization
- 🤖 AI Agriculture Chatbot (Gemini)
- 📚 Supported Crop Information
""")

# ------------------------------------
# HOW IT WORKS
# ------------------------------------
st.subheader("⚙️ How It Works")

st.markdown("""
1. Upload a clear leaf image.
2. The computer vision model analyzes the uploaded image.
3. The disease detection/classification model predicts the disease.
4. The prediction and confidence score are displayed.
5. **Ollama + LLM** provides AI-assisted information about the detected disease.
""")

# ------------------------------------
# BEST RESULTS
# ------------------------------------
st.info("""
### 📌 Best Results

✅ Use bright natural lighting

✅ Capture only one leaf

✅ Avoid blurry images

✅ Use a plain background

✅ Keep the leaf in the center of the image
""")

st.markdown("---")

st.success("👉 Click **Upload and Classify** from the left sidebar to start.")