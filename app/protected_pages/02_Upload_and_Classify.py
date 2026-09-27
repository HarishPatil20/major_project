
import streamlit as st
from PIL import Image

from utils.pipeline.inference import InferencePipeline
from utils.adviser_matching import get_adviser_recommendations
from utils.visuals.uncertainty_badge import render_uncertainty_badge
from utils.visuals.radar_plot import radar_chart
from utils.theme import apply_premium_theme
from utils.treatment_info import get_treatment_info


# ==========================================================
# PAGE CONFIG
# ==========================================================

apply_premium_theme()


# ==========================================================
# SESSION STATE
# ==========================================================

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_uploaded_image" not in st.session_state:
    st.session_state.last_uploaded_image = None

# Bumped whenever the user clears a scan - changing the file_uploader /
# camera_input widget's key makes Streamlit treat it as a brand-new
# widget, which is what actually clears a previously selected image
# (session_state alone does not reset those widgets).
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


def clear_current_scan():
    """Reset the scan result and force fresh upload/camera widgets."""
    st.session_state.last_result = None
    st.session_state.last_uploaded_image = None
    st.session_state.uploader_key += 1


st.markdown(
    """
    <style>
    .stApp { background: #f4f6f0; }
    .classify-hero {
        background: linear-gradient(135deg, #1E5620 0%, #2D7D32 60%, #E5A93C 100%);
        color: white;
        padding: 30px clamp(20px, 4vw, 40px);
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 12px 30px rgba(30, 86, 32, 0.2);
    }
    .classify-hero h1 { margin: 0; font-size: clamp(26px, 4vw, 40px); font-weight: 800; }
    .classify-hero p { margin: 8px 0 0; color: #F5F5DC; font-size: 15px; }

    /* ==================================================
       AI DIAGNOSTIC RESULTS PANEL — dark "clinical" theme
       Applied only around the prediction results, purely
       visual: no result values are changed by this CSS.

       These target real st.container(key=...) wrapper elements
       (a stable ".st-key-<key>" class Streamlit adds to the actual
       DOM parent of that container's contents) rather than manual
       <div> tags split across separate st.markdown() calls — each
       st.markdown() call is parsed independently by Streamlit, so
       an unclosed tag there never really wraps later widgets; it
       only produced an empty, isolated styled box.
       ================================================== */
    .st-key-diag_wrapper {
        background: #0F172A;
        border-radius: 24px;
        padding: clamp(14px, 2vw, 24px);
        margin-top: 4px;
        box-shadow: 0 18px 44px rgba(15, 23, 42, 0.35);
    }
    .st-key-diag_wrapper h1, .st-key-diag_wrapper h2, .st-key-diag_wrapper h3,
    .st-key-diag_wrapper h4, .st-key-diag_wrapper h5, .st-key-diag_wrapper h6,
    .st-key-diag_wrapper p, .st-key-diag_wrapper label,
    .st-key-diag_wrapper [data-testid="stMarkdownContainer"],
    .st-key-diag_wrapper [data-testid="stMarkdownContainer"] p,
    .st-key-diag_wrapper [data-testid="stMarkdownContainer"] strong {
        color: #F1F5F9 !important;
    }
    .st-key-diag_wrapper [data-testid="stImage"] figcaption { color: #94A3B8 !important; }
    div[class*="st-key-diag_card_"] {
        background: linear-gradient(160deg, #1E293B 0%, #172033 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: clamp(12px, 1.8vw, 18px);
        margin-bottom: 14px;
    }
    .st-key-diag_wrapper [data-testid="stImage"] img {
        border-radius: 12px;
    }
    .st-key-diag_wrapper hr { margin: 10px 0 !important; }

    /* ==================================================
       NEW SCAN CARD — upload / camera input area
       ================================================== */
    .st-key-upload_zone {
        background: linear-gradient(160deg, #ffffff 0%, #F7FAF3 100%);
        border: 1.5px dashed #2D7D32;
        border-radius: 20px;
        padding: clamp(16px, 2.6vw, 28px);
        margin-bottom: 18px;
        box-shadow: 0 6px 18px rgba(30, 86, 32, 0.08);
    }
    .upload-zone-title {
        font-size: 19px;
        font-weight: 800;
        color: #1E5620;
        margin-bottom: 2px;
    }
    .upload-zone-subtitle {
        font-size: 13px;
        color: #4B5A45;
        margin-bottom: 14px;
    }
    .st-key-upload_zone [data-testid="stFileUploaderDropzone"] {
        border-radius: 14px;
        border: 1.5px solid #C9DDC2;
        background: #FBFDF8;
    }
    .st-key-upload_zone div[role="radiogroup"] {
        gap: 6px;
    }
    .st-key-upload_zone div[role="radiogroup"] label {
        border: 1.5px solid #C9DDC2;
        border-radius: 999px;
        padding: 6px 16px;
        background: #ffffff;
        transition: all 0.15s ease;
    }
    .st-key-upload_zone div[role="radiogroup"] label:hover {
        border-color: #2D7D32;
        background: #F0F7EC;
    }

    /* Camera "Take Photo" / "Clear photo" buttons and the file
       uploader's "Browse files" button — restyled to match the
       app's green theme instead of Streamlit's plain grey default. */
    .st-key-upload_zone button {
        background: linear-gradient(135deg, #1E5620, #2D7D32) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 700 !important;
        padding: 8px 22px !important;
        box-shadow: 0 4px 12px rgba(30, 86, 32, 0.25) !important;
        transition: all 0.15s ease !important;
    }
    .st-key-upload_zone button:hover {
        background: linear-gradient(135deg, #2D7D32, #1E5620) !important;
        box-shadow: 0 6px 16px rgba(30, 86, 32, 0.35) !important;
        transform: translateY(-1px);
    }
    .st-key-upload_zone button p { color: #ffffff !important; }
    .st-key-upload_zone [data-testid="stCameraInput"] video,
    .st-key-upload_zone [data-testid="stCameraInput"] img {
        border-radius: 14px;
        border: 1.5px solid #C9DDC2;
    }

    /* Clear & scan-new button — solid red, unmissable, clearly a
       destructive/reset action next to the green "Prediction
       Complete" banner. */
    .st-key-clear_scan_btn { margin-top: 6px; }
    .st-key-clear_scan_btn button {
        background: linear-gradient(135deg, #E63946, #B3261E) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 800 !important;
        padding: 10px 18px !important;
        box-shadow: 0 4px 14px rgba(179, 38, 30, 0.35) !important;
        transition: all 0.15s ease !important;
    }
    .st-key-clear_scan_btn button:hover {
        background: linear-gradient(135deg, #B3261E, #8C1D16) !important;
        box-shadow: 0 6px 18px rgba(179, 38, 30, 0.45) !important;
        transform: translateY(-1px);
    }
    .st-key-clear_scan_btn button p { color: #ffffff !important; }

    /* Compact stat tiles used in the Model Confidence Summary */
    .st-key-diag_wrapper [data-testid="stMetric"] {
        background: rgba(148, 163, 184, 0.08);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 10px 14px;
    }
    .st-key-diag_wrapper [data-testid="stMetricLabel"] { font-size: 12px !important; }
    .diag-card-title {
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 10px;
        display: inline-block;
    }
    .st-key-diag_wrapper .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    .diag-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        color: white;
        margin: 6px 0 2px;
    }
    .diag-badge-low { background: linear-gradient(135deg, #4ECDC4, #44A08D); }
    .diag-badge-medium { background: #FFB703; color: #221a00; }
    .diag-badge-high { background: linear-gradient(135deg, #FF6B6B, #E63946); }

    .treatment-box {
        border-radius: 14px;
        padding: 16px 18px;
        margin-top: 10px;
        border-left: 5px solid #4ECDC4;
        background: rgba(78, 205, 196, 0.08);
    }
    .treatment-box.treatment-none {
        border-left-color: #64748B;
        background: rgba(100, 116, 139, 0.08);
    }
    .treatment-medicine-name {
        font-size: 15px;
        font-weight: 800;
        color: #F1F5F9 !important;
        margin-bottom: 4px;
    }
    .treatment-buy-link {
        display: inline-block;
        margin-top: 10px;
        padding: 8px 16px;
        border-radius: 999px;
        background: linear-gradient(135deg, #1E5620, #2D7D32);
        color: #ffffff !important;
        font-size: 13px;
        font-weight: 700;
        text-decoration: none !important;
    }
    </style>
    <div class="classify-hero">
        <h1>🌿 Crop Disease Scanner & Classification</h1>
        <p>Upload a leaf image or capture a photo using your camera for instant AI diagnostics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def severity_badge_html(disease_name: str, confidence: float) -> str:
    """Purely presentational confidence-based badge.

    Derived only from the model's own already-computed disease name and
    confidence value — does not run any additional inference and never
    changes what is displayed elsewhere on the page.
    """
    if "healthy" in disease_name.lower():
        label, css_class = "Low / Healthy", "diag-badge-low"
    elif confidence >= 0.66:
        label, css_class = "High Confidence", "diag-badge-high"
    elif confidence >= 0.35:
        label, css_class = "Medium Confidence", "diag-badge-medium"
    else:
        label, css_class = "Low Confidence", "diag-badge-low"
    return f'<span class="diag-badge {css_class}">{label}</span>'


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


img = None

with st.container(key="upload_zone"):

    st.markdown(
        '<div class="upload-zone-title">📤 New Scan</div>'
        '<div class="upload-zone-subtitle">'
        'Pick a crop, then upload a photo or capture one live.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ==================================================
    # CROP SELECTION
    # ==================================================

    crop_type = st.selectbox(

        "🌱 Choose the crop",

        [
            "Arecanut",
            "Rice",
            "Corn"
        ]
    )


    # ==================================================
    # INPUT METHOD
    # ==================================================

    input_method = st.radio(

        "📷 Choose how you want to provide the image",

        [
            "📁 Upload Image",
            "📸 Live Camera"
        ],

        horizontal=True
    )


    # ==================================================
    # UPLOAD IMAGE
    # ==================================================

    if input_method == "📁 Upload Image":

        uploaded = st.file_uploader(

            "Drag and drop, or browse for a crop image",

            type=[
                "jpg",
                "jpeg",
                "png",
                "webp"
            ],

            key=f"file_uploader_{st.session_state.uploader_key}"
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

                preview_columns = st.columns([1, 2, 1])

                with preview_columns[1]:

                    st.image(

                        img,

                        caption="🖼️ Uploaded Image",

                        width=260
                    )


    # ==================================================
    # LIVE CAMERA
    # ==================================================

    elif input_method == "📸 Live Camera":

        st.info(
            "📸 Allow camera permission in your browser "
            "when prompted."
        )


        camera_photo = st.camera_input(

            "Capture Crop Image",

            key=f"camera_input_{st.session_state.uploader_key}"
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

                preview_columns = st.columns([1, 2, 1])

                with preview_columns[1]:

                    st.image(

                        img,

                        caption="📷 Captured Camera Image",

                        width=260
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

    result_header_columns = st.columns([2, 1])

    with result_header_columns[0]:
        st.success(
            "✅ Prediction Complete"
        )

    with result_header_columns[1]:
        with st.container(key="clear_scan_btn"):
            if st.button(
                "🗑️ Clear & Scan New",
                use_container_width=True,
            ):
                clear_current_scan()
                st.rerun()

    with st.container(key="diag_wrapper"):
      with st.container(key="diag_card_1"):
        st.markdown('<div class="diag-card-title">🎯 Scan Results</div>', unsafe_allow_html=True)

        # ======================================================
        # NO-DETECTION FALLBACK NOTICE
        # ======================================================

        detection_found = result.get("detection_found", True)

        if not detection_found:
            st.warning(
                "⚠️ No specific region (leaf/nut/trunk) was detected in "
                "this image with high confidence, so the **whole image** "
                "was classified directly instead. For a more precise "
                "result, try a clearer, closer photo of the affected part."
            )

        # ======================================================
        # BOUNDING BOX
        # ======================================================

        result_image_columns = st.columns(2)

        if "boxed_image" in result:
            with result_image_columns[0]:
                st.markdown("**🎯 Detected Region**")
                st.image(
                    result["boxed_image"],
                    caption=(
                        "YOLO11 Detected Region"
                        if detection_found
                        else "No region detected (full image shown)"
                    ),
                    width=240
                )

        if "cropped_image" in result:
            with result_image_columns[1]:
                st.markdown("**🌿 Cropped Region**")
                st.image(
                    result["cropped_image"],
                    caption=(
                        "Region Used for Analysis"
                        if detection_found
                        else "Full image used (fallback)"
                    ),
                    width=240
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

      with st.container(key="diag_card_2"):


        # ======================================================
        # ADVISER RECOMMENDATIONS
        # ======================================================

        disease = result.get("disease", "Unknown")
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
        # SUGGESTED TREATMENT (purely additive — presentational
        # only, derived from the disease already predicted above;
        # never re-runs or alters any model inference/value).
        # ======================================================

        st.markdown("---")
        st.subheader("💊 Suggested Treatment")

        treatment = get_treatment_info(species, disease)

        if treatment["available"]:
            st.markdown(
                f"""
                <div class="treatment-box">
                    <div class="treatment-medicine-name">🧪 {treatment['medicine']}</div>
                    <div>{treatment['advice']}</div>
                    <a class="treatment-buy-link" href="{treatment['buy_url']}" target="_blank">🛒 Search to Buy →</a>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="treatment-box treatment-none">
                    <div class="treatment-medicine-name">{treatment['disease']}</div>
                    <div>{treatment['advice']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

      with st.container(key="diag_card_3"):


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

            (
                f"**Confidence (no region detected — "
                f"whole-image classification):** "
                if not detection_found
                else f"**Confidence:** "
            )
            + f"{disease_conf * 100:.2f}%"
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

        st.markdown(severity_badge_html(disease, disease_conf), unsafe_allow_html=True)


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


            heatmap_columns = st.columns([1, 2, 1])

            with heatmap_columns[1]:

                st.image(

                    result["heatmap"],

                    caption="Model Focus Area",

                    width=320
                )

      with st.container(key="diag_card_4"):


        # ======================================================
        # CONFIDENCE SUMMARY
        # ======================================================

        st.markdown(
            '<div class="diag-card-title">📊 Model Confidence Summary</div>',
            unsafe_allow_html=True,
        )


        mc_uncertainty = float(
            result.get("mc_uncertainty", 0)
        )

        tta_uncertainty = float(
            result.get("tta_uncertainty", 0)
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Disease Confidence", f"{disease_conf:.4f}")

        with col2:
            st.metric("MC Uncertainty", f"{mc_uncertainty:.4f}")

        with col3:
            st.metric("TTA Uncertainty", f"{tta_uncertainty:.4f}")


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


            radar_columns = st.columns([1, 2, 1])

            with radar_columns[1]:

                st.pyplot(

                    radar_fig,

                    width=320
                )

      with st.container(key="diag_card_5"):


        # ======================================================
        # PLANT STATUS
        # ======================================================

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

