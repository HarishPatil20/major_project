"""
Suggested treatment / medicine information for detected crop diseases.

This is a PURELY additive, presentational lookup table used only to show
farmers a suggested treatment and a "search to buy" link after a disease
has already been detected. It never runs any inference and never changes
any detection/classification value shown elsewhere on the page.

Keys are deliberately the exact disease label strings produced by the live
YOLO pipeline (see utils/pipeline/inference.py -> InferencePipeline.class_names),
NOT the older/unused utils/species_mapping.py labels, which belong to a
different, disconnected legacy model and do not match what this app
actually predicts.
"""

from urllib.parse import quote_plus

# ----------------------------------------------------------------------
# (crop, disease label) -> treatment info
# ----------------------------------------------------------------------
TREATMENT_INFO = {

    # ================= RICE =================
    ("Rice", "Bacterial Leaf Blight"): {
        "medicine": "Copper oxychloride 50% WP or Streptocycline (Streptomycin sulfate) spray",
        "advice": "Drain the field, avoid excess nitrogen, and spray at the first sign of water-soaked lesions. Use resistant varieties next season where possible.",
    },
    ("Rice", "Brown Spot"): {
        "medicine": "Mancozeb 75% WP or Propiconazole 25% EC fungicide",
        "advice": "Improve soil potassium/nutrient balance and treat seeds before sowing to reduce recurrence.",
    },
    ("Rice", "Leaf Blast"): {
        "medicine": "Tricyclazole 75% WP fungicide",
        "advice": "Avoid excess nitrogen fertilizer, keep proper water levels, and spray at early tillering if lesions appear.",
    },
    ("Rice", "Leaf Scald"): {
        "medicine": "Propiconazole 25% EC or Azoxystrobin-based fungicide",
        "advice": "Ensure balanced fertilization and avoid dense planting to improve airflow.",
    },
    ("Rice", "Narrow Brown Leaf Spot"): {
        "medicine": "Mancozeb 75% WP fungicide",
        "advice": "Maintain balanced potassium levels and remove infected crop residue after harvest.",
    },
    ("Rice", "Neck Blast"): {
        "medicine": "Tricyclazole 75% WP or Isoprothiolane fungicide",
        "advice": "Spray preventively at panicle initiation and again at heading in blast-prone fields.",
    },
    ("Rice", "Rice Hispa"): {
        "medicine": "Chlorpyrifos 20% EC or Neem oil-based insecticide",
        "advice": "Clip and destroy affected leaf tips; avoid excess nitrogen which attracts hispa beetles.",
    },
    ("Rice", "Healthy Leaf"): {
        "medicine": None,
        "advice": "No disease detected — keep up your current field management practices.",
    },

    # ------------------------------------------------------------------
    # Additional Rice classes from the Rice classification refinement
    # model (utils/pipeline/inference.py ->
    # classification_model_paths["Rice"]). These class names come
    # straight from that model's own training labels, which differ
    # slightly from the detection-model class names above (e.g.
    # "Neck_Blast" vs "Neck Blast"), so they need their own entries.
    # ------------------------------------------------------------------
    ("Rice", "Healthy Rice Leaf"): {
        "medicine": None,
        "advice": "No disease detected — keep up your current field management practices.",
    },
    ("Rice", "Leaf scald"): {
        "medicine": "Propiconazole 25% EC or Azoxystrobin-based fungicide",
        "advice": "Ensure balanced fertilization and avoid dense planting to improve airflow.",
    },
    ("Rice", "Neck_Blast"): {
        "medicine": "Tricyclazole 75% WP or Isoprothiolane fungicide",
        "advice": "Spray preventively at panicle initiation and again at heading in blast-prone fields.",
    },
    ("Rice", "Sheath Blight"): {
        "medicine": "Hexaconazole 5% SC or Validamycin 3% L fungicide",
        "advice": "Avoid excess nitrogen and dense planting, drain the field periodically, and remove infected stubble after harvest to reduce the fungus (Rhizoctonia solani) carrying over to the next crop.",
    },
    ("Rice", "Tungro"): {
        "medicine": "No curative treatment — control the green leafhopper vector with Imidacloprid or Thiamethoxam-based insecticide",
        "advice": "This is a viral disease spread by green leafhoppers, not a fungus, so it cannot be cured once infected. Remove and destroy infected plants early, use resistant varieties, and control the leafhopper population to prevent spread.",
    },

    # ================= CORN =================
    ("Corn", "Brown Spot"): {
        "medicine": "Mancozeb 75% WP or Azoxystrobin fungicide",
        "advice": "Rotate crops and avoid overhead irrigation late in the day to reduce leaf wetness.",
    },
    ("Corn", "Corn Rust"): {
        "medicine": "Propiconazole 25% EC or Azoxystrobin-based fungicide",
        "advice": "Plant rust-resistant hybrids where available and monitor closely during humid weather.",
    },
    ("Corn", "Corn Smut"): {
        "medicine": "Remove and destroy galls before they rupture; Propiconazole fungicide as a preventive spray",
        "advice": "Avoid mechanical injury to plants and rotate with non-host crops.",
    },
    ("Corn", "Downy Mildew"): {
        "medicine": "Metalaxyl + Mancozeb combination fungicide",
        "advice": "Use treated seed and avoid waterlogged fields; remove infected plants early.",
    },
    ("Corn", "Grey Leaf Spot"): {
        "medicine": "Azoxystrobin or Pyraclostrobin-based fungicide",
        "advice": "Practice crop rotation and residue management; resistant hybrids reduce severity.",
    },
    ("Corn", "Leaf Blight"): {
        "medicine": "Mancozeb 75% WP or Propiconazole 25% EC fungicide",
        "advice": "Remove infected debris after harvest and avoid dense planting for better airflow.",
    },
    ("Corn", "Healthy"): {
        "medicine": None,
        "advice": "No disease detected — keep up your current field management practices.",
    },

    # ------------------------------------------------------------------
    # Additional Corn classes from the Corn classification refinement
    # model (utils/pipeline/inference.py ->
    # classification_model_paths["Corn"]). These class names come
    # straight from that model's own training labels, which differ from
    # the detection-model class names above, so they need their own
    # entries.
    # ------------------------------------------------------------------
    ("Corn", "Blight"): {
        "medicine": "Mancozeb 75% WP or Propiconazole 25% EC fungicide",
        "advice": "Remove infected debris after harvest and avoid dense planting for better airflow.",
    },
    ("Corn", "Common_Rust"): {
        "medicine": "Propiconazole 25% EC or Azoxystrobin-based fungicide",
        "advice": "Plant rust-resistant hybrids where available and monitor closely during humid weather.",
    },
    ("Corn", "Gray_Leaf_Spot"): {
        "medicine": "Azoxystrobin or Pyraclostrobin-based fungicide",
        "advice": "Practice crop rotation and residue management; resistant hybrids reduce severity.",
    },

    # ================= ARECANUT =================
    ("Arecanut", "Bud Borer"): {
        "medicine": "Chlorpyrifos 20% EC or Neem-based bio-pesticide (bud/crown drenching)",
        "advice": "Remove and destroy affected buds; maintain field sanitation to reduce pest carry-over.",
    },
    ("Arecanut", "Mahali Koleroga"): {
        "medicine": "1% Bordeaux mixture (Copper sulfate + lime) spray",
        "advice": "Spray before monsoon onset and repeat after heavy rain; ensure good drainage in the plantation.",
    },
    ("Arecanut", "Stem Bleeding"): {
        "medicine": "Bordeaux paste on cleaned wound + Tridemorph or Metalaxyl drenching",
        "advice": "Scrape the affected bark, apply fungicidal paste, and improve drainage around the base.",
    },
    ("Arecanut", "Stem Cracking"): {
        "medicine": "Bordeaux paste application and balanced boron/micronutrient supplementation",
        "advice": "Avoid water stress and ensure balanced nutrition to reduce cracking.",
    },
    ("Arecanut", "Yellow Leaf Disease"): {
        "medicine": "No curative chemical treatment — apply balanced NPK + micronutrients (especially Zinc, Magnesium) to slow progression",
        "advice": "Remove and destroy severely affected palms to limit spread; this is a phytoplasma disease with no known cure.",
    },
    ("Arecanut", "Healthy Foot"): {
        "medicine": None,
        "advice": "No disease detected — keep up your current field management practices.",
    },
    ("Arecanut", "Healthy Leaf"): {
        "medicine": None,
        "advice": "No disease detected — keep up your current field management practices.",
    },
    ("Arecanut", "Healthy Nut"): {
        "medicine": None,
        "advice": "No disease detected — keep up your current field management practices.",
    },
    ("Arecanut", "Healthy Trunk"): {
        "medicine": None,
        "advice": "No disease detected — keep up your current field management practices.",
    },

    # ------------------------------------------------------------------
    # Additional Arecanut classes from the retrained classification
    # refinement model (utils/pipeline/inference.py ->
    # classification_model_paths["Arecanut"]). These class names come
    # straight from that model's own training labels, which differ from
    # the detection-model class names above, so they need their own
    # entries here.
    # ------------------------------------------------------------------
    ("Arecanut", "Good"): {
        "medicine": None,
        "advice": "No disease detected — keep up your current field management practices.",
    },
    ("Arecanut", "Chukke roga"): {
        "medicine": "Propiconazole 25% EC, Tebuconazole, or Hexaconazole (1 ml/litre) for the first spray, "
                    "followed by Propineb 70% WP (2 g/litre) 25-30 days later",
        "advice": "This is Leaf Spot Disease (a fungal disease caused by Colletotrichum), an active concern in "
                   "Karnataka arecanut plantations. Add a sticker/spreader (100-200 ml per 200 litres) to the "
                   "spray solution for better adherence, remove severely affected leaves, and coordinate spraying "
                   "with neighboring plantations for better control (per ICAR-CPCRI guidance).",
    },
    ("Arecanut", "Kole roga"): {
        "medicine": "1% Bordeaux mixture (Copper sulfate + lime) spray",
        "advice": "This is fruit rot disease (same as Mahali/Koleroga). Spray before monsoon onset and repeat "
                   "after heavy rain; ensure good drainage in the plantation.",
    },
    ("Arecanut", "Split nut"): {
        "medicine": "Balanced boron and potassium supplementation; no curative chemical spray",
        "advice": "Nut splitting is usually a physiological disorder linked to irregular soil moisture or "
                   "boron/potassium deficiency rather than a pathogen. Maintain consistent irrigation and a "
                   "balanced fertilizer schedule to reduce recurrence.",
    },
}


def _buy_search_url(medicine_name: str) -> str:
    """A safe, always-available 'search to buy' link.

    We deliberately do not hardcode a specific storefront/product page
    (which could go dead or be wrong for the user's region) — instead we
    build a generic shopping search query so the farmer can compare
    real, currently available sellers themselves.
    """
    query = quote_plus(f"buy {medicine_name} online India")
    return f"https://www.google.com/search?tbm=shop&q={query}"


def get_treatment_info(species: str, disease: str) -> dict:
    """Return suggested treatment info for a (species, disease) pair.

    Returns a dict with keys:
        - available (bool): whether a specific medicine/treatment is known
        - medicine (str | None): suggested medicine/treatment name
        - advice (str): short practical advice text
        - buy_url (str | None): a search link to help find/buy it, if available
        - disease (str): the disease name, always included so the UI can
          mention it even when no medicine is available
    """
    entry = TREATMENT_INFO.get((species, disease))

    if entry is None:
        # Unknown / unmapped label — be honest that we don't have specific
        # treatment info rather than guessing.
        return {
            "available": False,
            "medicine": None,
            "advice": "No specific treatment information is available for this result yet.",
            "buy_url": None,
            "disease": disease,
        }

    medicine = entry.get("medicine")

    if not medicine:
        return {
            "available": False,
            "medicine": None,
            "advice": entry.get("advice", ""),
            "buy_url": None,
            "disease": disease,
        }

    return {
        "available": True,
        "medicine": medicine,
        "advice": entry.get("advice", ""),
        "buy_url": _buy_search_url(medicine),
        "disease": disease,
    }
