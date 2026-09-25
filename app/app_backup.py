import streamlit as st

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="CropDoctor AI",
    page_icon="🌾",
    layout="wide"
)

# ==========================================================
# HEADER
# ==========================================================

st.title("🌾 CropDoctor AI")

st.subheader(
    "AI-Powered Rice Leaf Disease Detection & Farmer Assistant"
)

st.write(
    """
    CropDoctor AI helps farmers identify rice leaf diseases
    using an AI-based image detection system.
    Upload a clear rice leaf image and get the predicted disease
    with a confidence score and bounding box.
    """
)

st.markdown("---")

# ==========================================================
# FOR FARMERS
# ==========================================================

st.header("👨‍🌾 For Farmers")

st.write(
    """
    This application is designed to make crop disease detection
    simple and easy for farmers.

    You do not need technical knowledge to use the application.
    Just upload a clear image of a rice leaf and check the result.
    """
)

# ==========================================================
# HOW TO USE
# ==========================================================

st.header("📱 How to Use the App")

st.markdown(
    """
    **Step 1 — Upload Leaf Image 📸**

    Go to **Upload & Classify** and upload a clear rice leaf image.

    **Step 2 — Detect Disease 🔍**

    Click **Detect & Classify Disease**.

    **Step 3 — Check Bounding Box 🎯**

    The AI identifies the leaf/disease region using a bounding box.

    **Step 4 — Check Disease 🦠**

    The application shows the predicted rice disease.

    **Step 5 — Check Confidence 📊**

    Check the confidence percentage of the prediction.

    **Step 6 — Get Agriculture Information 💬**

    Use **Talk to Our Chatbot** to ask agriculture and
    plant-disease-related questions.
    """
)

st.markdown("---")

# ==========================================================
# AI WORKFLOW
# ==========================================================

st.header("🤖 How CropDoctor AI Works")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("📸\n\nUpload Image")

with col2:
    st.info("🎯\n\nYOLO11n Detection")

with col3:
    st.info("🦠\n\nDisease Prediction")

with col4:
    st.info("📊\n\nConfidence Result")

st.markdown("---")

# ==========================================================
# CURRENT MODEL
# ==========================================================

st.header("🧠 AI Model")

st.write(
    """
    **YOLO11n Rice Disease Detector**

    The current Rice disease module uses YOLO11n to detect
    and classify rice leaf diseases and display the detected
    region using a bounding box.
    """
)

# ==========================================================
# SUPPORTED RICE DISEASES
# ==========================================================

st.header("🌾 Supported Rice Conditions")

diseases = [
    "Bacterial Leaf Blight",
    "Brown Spot",
    "Healthy Leaf",
    "Leaf Blast",
    "Leaf Scald",
    "Narrow Brown Leaf Spot",
    "Neck Blast",
    "Rice Hispa"
]

for disease in diseases:
    st.write(f"• {disease}")

st.markdown("---")

# ==========================================================
# OTHER FEATURES
# ==========================================================

st.header("🌱 Other Features")

col1, col2 = st.columns(2)

with col1:
    st.success(
        """
        🌿 **Upload & Classify**

        Detect rice leaf disease using an AI model.
        """
    )

    st.success(
        """
        💬 **AI Chatbot**

        Ask agriculture and plant disease questions.
        """
    )

with col2:
    st.success(
        """
        🌦️ **Live Weather**

        Check weather information for farming decisions.
        """
    )

    st.success(
        """
        📈 **Live Market Prices**

        Check crop/market price information.
        """
    )

st.markdown("---")

# ==========================================================
# SIMPLE MESSAGE
# ==========================================================

st.header("✅ Easy for Farmers")

st.write(
    """
    CropDoctor AI is designed with a simple interface so that
    farmers can upload an image, understand the disease result,
    and use the available agriculture features without
    complicated technical steps.
    """
)

st.warning(
    "⚠️ AI predictions are for assistance. For serious crop "
    "disease problems, consult a local agriculture expert."
)