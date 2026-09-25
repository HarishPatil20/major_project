import streamlit as st
from PIL import Image

from utils.pipeline.inference import InferencePipeline
from utils.visuals.uncertainty_badge import render_uncertainty_badge
from utils.visuals.radar_plot import radar_chart


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(

    page_title="Upload & Classify",

    page_icon="🌿",

    layout="wide"
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "last_result" not in st.session_state:

    st.session_state.last_result = None


if "last_uploaded_image" not in st.session_state:

    st.session_state.last_uploaded_image = None


# ==========================================================
# TITLE
# ==========================================================

st.title("🌿 Upload & Classify")

st.write(

    "Upload a crop leaf image and select the crop "
    "to identify possible diseases."
)


# ==========================================================
# LOAD PIPELINE
# ==========================================================

@st.cache_resource
def load_pipeline():

    try:

        return InferencePipeline(
            device="cpu"
        )

    except Exception as e:

        st.error(
            "❌ Model files are not available."
        )

        st.exception(e)

        st.stop()


pipeline = load_pipeline()


# ==========================================================
# CROP SELECTION
# ==========================================================

st.subheader("🌱 Select Crop")

crop_type = st.selectbox(

    "Choose the crop",

    [
        "Rice",
        "Corn"
    ]
)


# ==========================================================
# FILE UPLOADER
# ==========================================================

uploaded = st.file_uploader(

    "📸 Upload a leaf image",

    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)


# ==========================================================
# PREDICTION
# ==========================================================

if uploaded is not None:

    img = Image.open(
        uploaded
    ).convert("RGB")

    st.subheader(
        "Uploaded Image"
    )

    st.image(

        img,

        caption="Uploaded Image",

        width="stretch"
    )

    st.markdown("---")

    if st.button(

        "🔍 Detect & Classify Disease",

        type="primary"
    ):

        with st.spinner(

            f"Analyzing {crop_type} leaf..."
        ):

            try:

                result = pipeline.predict(

                    img,

                    crop_type=crop_type
                )

            except Exception as e:

                st.error(
                    "❌ Prediction failed."
                )

                st.exception(e)

                st.stop()

        # ==================================================
        # ERROR CHECK
        # ==================================================

        if not result or "error" in result:

            st.error(

                result.get(

                    "error",

                    "No prediction was returned."
                )
            )

            st.stop()

        # ==================================================
        # SAVE RESULT
        # ==================================================

        st.session_state.last_uploaded_image = img

        st.session_state.last_result = result


# ==========================================================
# DISPLAY RESULT
# ==========================================================

result = st.session_state.last_result


if result is not None:

    st.success(
        "✅ Prediction Complete"
    )

    # ======================================================
    # BOUNDING BOX
    # ======================================================

    if "boxed_image" in result:

        st.subheader(
            "🎯 Detected Leaf Bounding Box"
        )

        st.image(

            result["boxed_image"],

            caption="Detected Leaf Bounding Box",

            width="stretch"
        )

    # ======================================================
    # CROPPED LEAF
    # ======================================================

    if "cropped_image" in result:

        st.subheader(
            "🌿 Cropped Leaf Region"
        )

        st.image(

            result["cropped_image"],

            caption="Cropped Leaf for Classification",

            width="stretch"
        )

    st.markdown("---")

    # ======================================================
    # SPECIES / CROP
    # ======================================================

    st.subheader(
        "🌱 Crop Prediction"
    )

    species = result.get(

        "species",

        "Unknown"
    )

    species_conf = float(

        result.get(

            "species_conf",

            0
        )
    )

    st.write(

        f"**Predicted Crop:** {species}"
    )

    st.write(

        f"**Detection Confidence:** "
        f"{species_conf * 100:.2f}%"
    )

    st.progress(

        max(

            0.0,

            min(

                1.0,

                species_conf
            )
        )
    )

    # ======================================================
    # DISEASE
    # ======================================================

    st.subheader(
        "🦠 Disease Prediction"
    )

    disease = result.get(

        "disease",

        "Unknown"
    )

    disease_conf = float(

        result.get(

            "disease_conf",

            0
        )
    )

    if "healthy" in disease.lower():

        st.success(

            f"🟢 Healthy Leaf"
        )

    else:

        st.error(

            f"🔴 Disease: {disease}"
        )

    st.write(

        f"**Confidence:** "
        f"{disease_conf * 100:.2f}%"
    )

    st.progress(

        max(

            0.0,

            min(

                1.0,

                disease_conf
            )
        )
    )

    # ======================================================
    # MODEL USED
    # ======================================================

    if "model_used" in result:

        st.write(

            f"**Model Used:** "
            f"`{result['model_used']}`"
        )

    # ======================================================
    # GRAD-CAM
    # ======================================================

    if (

        "heatmap" in result

        and result["heatmap"] is not None
    ):

        st.subheader(

            "🔥 Model Explainability"
        )

        st.image(

            result["heatmap"],

            caption="Model Focus Area",

            width="stretch"
        )

    # ======================================================
    # CONFIDENCE SUMMARY
    # ======================================================

    st.markdown("---")

    st.subheader(

        "📊 Model Confidence Summary"
    )

    col1, col2, col3 = st.columns(3)

    # ------------------------------------------------------
    # Disease Confidence
    # ------------------------------------------------------

    with col1:

        st.write(
            "**Disease Confidence**"
        )

        st.write(

            f"{disease_conf:.4f}"
        )

    # ------------------------------------------------------
    # MC Uncertainty
    # ------------------------------------------------------

    with col2:

        mc_uncertainty = float(

            result.get(

                "mc_uncertainty",

                0
            )
        )

        st.write(

            "**MC Uncertainty**"
        )

        st.write(

            f"{mc_uncertainty:.4f}"
        )

    # ------------------------------------------------------
    # TTA Uncertainty
    # ------------------------------------------------------

    with col3:

        tta_uncertainty = float(

            result.get(

                "tta_uncertainty",

                0
            )
        )

        st.write(

            "**TTA Uncertainty**"
        )

        st.write(

            f"{tta_uncertainty:.4f}"
        )

    # ======================================================
    # UNCERTAINTY BADGE
    # ======================================================

    if "uncertainty_fused" in result:

        render_uncertainty_badge(

            result["uncertainty_fused"]
        )

    # ======================================================
    # RADAR CHART
    # ======================================================

    if all(

        key in result

        for key in [

            "disease_conf",

            "mc_uncertainty",

            "tta_uncertainty",

            "uncertainty_fused"
        ]
    ):

        st.markdown("---")

        st.subheader(

            "📈 Model Reliability Radar Chart"
        )

        radar_fig = radar_chart(

            result["disease_conf"],

            result["mc_uncertainty"],

            result["tta_uncertainty"],

            result["uncertainty_fused"]
        )

        st.pyplot(

            radar_fig,

            width="stretch"
        )

    # ======================================================
    # PLANT STATUS
    # ======================================================

    st.markdown("---")

    st.subheader(
        "🌿 Plant Status"
    )

    if "healthy" in disease.lower():

        st.success(

            "🟢 Healthy — No major disease detected."
        )

    elif disease != "Unknown":

        st.error(

            f"🔴 Diseased — {disease}"
        )

    # ======================================================
    # TIPS
    # ======================================================

    with st.expander(

        "📸 Tips for Better Predictions"
    ):

        st.write(

            """
            • Use a clear leaf image

            • Use good lighting

            • Avoid blurry images

            • Avoid heavy shadows

            • Keep the leaf clearly visible

            • Prefer one leaf in the image
            """
        )