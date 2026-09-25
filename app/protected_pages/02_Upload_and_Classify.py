
import streamlit as st
from PIL import Image

from utils.pipeline.inference import InferencePipeline
from utils.adviser_matching import get_adviser_recommendations
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
    "Upload an image or use your live camera to "
    "detect and classify crop diseases."
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
        "Arecanut",
        "Rice",
        "Corn"
    ]
)


# ==========================================================
# INPUT METHOD
# ==========================================================

st.subheader("📷 Select Input Method")

input_method = st.radio(

    "Choose how you want to provide the image",

    [
        "📁 Upload Image",
        "📸 Live Camera"
    ],

    horizontal=True
)


img = None


# ==========================================================
# UPLOAD IMAGE
# ==========================================================

if input_method == "📁 Upload Image":

    uploaded = st.file_uploader(

        "📸 Upload a crop image",

        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ]
    )


    if uploaded is not None:

        try:

            img = Image.open(
                uploaded
            ).convert("RGB")

        except Exception as e:

            st.error(
                "❌ Could not read the image."
            )

            st.exception(e)


        if img is not None:

            st.subheader(
                "🖼️ Uploaded Image"
            )

            st.image(

                img,

                caption="Uploaded Image",

                width=320
            )


# ==========================================================
# LIVE CAMERA
# ==========================================================

elif input_method == "📸 Live Camera":

    st.info(
        "📸 Allow camera permission in your browser "
        "when prompted."
    )


    camera_photo = st.camera_input(

        "📷 Capture Crop Image"
    )


    if camera_photo is not None:

        try:

            img = Image.open(

                camera_photo
            ).convert("RGB")

        except Exception as e:

            st.error(
                "❌ Could not read camera image."
            )

            st.exception(e)


        if img is not None:

            st.subheader(
                "📷 Captured Camera Image"
            )

            st.image(

                img,

                caption="Captured Camera Image",

                width=320
            )


# ==========================================================
# PREDICTION BUTTON
# ==========================================================

if img is not None:

    st.markdown("---")

    if st.button(

        "🔍 Detect & Classify Disease",

        type="primary",

        use_container_width=True
    ):

        with st.spinner(

            f"Analyzing {crop_type}..."
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

    st.markdown("---")

    st.success(
        "✅ Prediction Complete"
    )


    # ======================================================
    # BOUNDING BOX
    # ======================================================

    result_image_columns = st.columns(2)

    if "boxed_image" in result:
        with result_image_columns[0]:
            st.subheader("🎯 Detected Region")
            st.image(
                result["boxed_image"],
                caption="YOLO11 Detected Region",
                width=300
            )

    if "cropped_image" in result:
        with result_image_columns[1]:
            st.subheader("🌿 Cropped Region")
            st.image(
                result["cropped_image"],
                caption="Region Used for Analysis",
                width=300
            )


    st.markdown("---")


    # ======================================================
    # CROP PREDICTION
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
    # ADVISER RECOMMENDATIONS
    # ======================================================

    advisers = get_adviser_recommendations(
        result.get("species", crop_type),
        disease,
    )

    st.subheader("👨‍🌾 Recommended Crop Advisers")

    if advisers:
        adviser_columns = st.columns(min(len(advisers), 3))
        for index, adviser in enumerate(advisers):
            with adviser_columns[index % len(adviser_columns)]:
                st.markdown(
                    f"**{adviser['full_name']}**  \n"
                    f"{adviser['specialization']}  \n"
                    f"📍 {adviser['location']}  \n"
                    f"📞 {adviser['phone']}"
                )
    else:
        st.info(
            "No adviser has been assigned for this crop or disease yet. "
            "An administrator can add one from the Admin Panel."
        )


    # ======================================================
    # CLASSIFICATION RESULT
    # ======================================================

    if "classification_result" in result:

        st.subheader(
            "🧠 Classification Result"
        )


        classification_name = result.get(

            "classification_result",

            "Unknown"
        )


        classification_conf = float(

            result.get(

                "classification_conf",

                0
            )
        )


        st.write(

            f"**Classification:** "
            f"{classification_name}"
        )


        st.write(

            f"**Classification Confidence:** "
            f"{classification_conf * 100:.2f}%"
        )


        st.progress(

            max(

                0.0,

                min(

                    1.0,

                    classification_conf
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
            "🟢 Healthy"
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
    # DETECTION RESULT
    # ======================================================

    if "detection_result" in result:

        st.write(

            f"**YOLO11 Detection:** "
            f"{result['detection_result']}"
        )


    if "detection_conf" in result:

        detection_conf = float(

            result["detection_conf"]
        )


        st.write(

            f"**YOLO11 Confidence:** "
            f"{detection_conf * 100:.2f}%"
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
    # GRAD-CAM / HEATMAP
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
            • Use a clear image of the arecanut plant

            • Use good lighting

            • Avoid blurry images

            • Avoid heavy shadows

            • Keep the affected region clearly visible

            • Prefer one main leaf / plant region

            • For camera mode, keep the phone steady
            """
        )

