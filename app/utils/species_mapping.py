import os

# ----------------------------------------------------
# Resolve project root (works no matter where imported)
# ----------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def p(rel_path: str) -> str:
    """Build absolute paths relative to project root."""
    return os.path.join(PROJECT_ROOT, rel_path)

# ----------------------------------------------------
# DATASET FOLDERS (train splits used to get class names)
# ----------------------------------------------------
# ----------------------------------------------------
# FIX: Dataset folders not included with project
# Manually defined class labels (demo / viva safe)
# ----------------------------------------------------

CASSAVA_LABELS = [
    "Cassava Bacterial Blight",
    "Cassava Brown Streak Disease",
    "Cassava Green Mottle",
    "Cassava Mosaic Disease",
    "Healthy"
]

# Sourced from the actual Rice classification model's own class names
# (utils/pipeline/inference.py loads models/rice_classification/best.pt,
# whose .names are exactly these 10 labels) - not a separate/invented list.
RICE_LABELS = [
    "Bacterial Leaf Blight",
    "Brown Spot",
    "Healthy Rice Leaf",
    "Leaf Blast",
    "Leaf scald",
    "Narrow Brown Leaf Spot",
    "Neck_Blast",
    "Rice Hispa",
    "Sheath Blight",
    "Tungro"
]

# Sourced from the actual Corn classification model's own class names
# (models/corn_classification/best.pt) - not a separate/invented list.
CORN_LABELS = [
    "Blight",
    "Common_Rust",
    "Gray_Leaf_Spot",
    "Healthy"
]

# Sourced from the actual Arecanut detection model (Bud Borer, Yellow Leaf
# Disease, Mahali Koleroga, Stem Bleeding, Stem Cracking) and the Arecanut
# nut-classification model (Chukke Roga, Split Nut) already wired up in
# utils/pipeline/inference.py - not a separate/invented disease list.
ARECANUT_LABELS = [
    "Bud Borer",
    "Yellow Leaf Disease",
    "Mahali Koleroga (Kole Roga)",
    "Stem Bleeding",
    "Stem Cracking",
    "Chukke Roga",
    "Split Nut",
    "Healthy"
]

PLANTVILLAGE_LABELS = [
    "Pepper Bell Bacterial Spot",
    "Pepper Bell Healthy",
    "Potato Early Blight",
    "Potato Late Blight",
    "Potato Healthy",
    "Tomato Bacterial Spot",
    "Tomato Early Blight",
    "Tomato Late Blight",
    "Tomato Leaf Mold",
    "Tomato Septoria Leaf Spot",
    "Tomato Spider Mites",
    "Tomato Target Spot",
    "Tomato Yellow Leaf Curl Virus",
    "Tomato Mosaic Virus",
    "Tomato Healthy"
]

# ----------------------------------------------------
# SPECIES LIST (MUST match species classifier training order)
# ----------------------------------------------------
SPECIES_LIST = [
    "Apple",
    "Blueberry",
    "Cassava",
    "Cherry_(including_sour)",
    "Corn_(maize)",
    "Grape",
    "Orange",
    "Peach",
    "Pepper_bell",
    "Potato",
    "Raspberry",
    "Rice",
    "Soybean",
    "Squash",
    "Strawberry",
    "Tomato",
]

# ----------------------------------------------------
# SPECIES → DISEASE MODEL KEY
# (three model keys: 'Cassava', 'Rice', 'PlantVillage')
# ----------------------------------------------------
SPECIES_TO_MODEL_KEY = {
    "Cassava": "Cassava",
    "Rice": "Rice",
}

# All non-Cassava, non-Rice species → PlantVillage model
for sp in SPECIES_LIST:
    if sp not in SPECIES_TO_MODEL_KEY:
        SPECIES_TO_MODEL_KEY[sp] = "PlantVillage"

# ----------------------------------------------------
# DISEASE MODEL FILE PATHS (three models total)
# ----------------------------------------------------
DISEASE_MODEL_PATHS = {
    "Cassava": p("models/cassava_best.pth"),
    "Rice": p("models/rice_leaf_best.pth"),
    "PlantVillage": p("models/plant_village_best.pth"),
}

# ----------------------------------------------------
# MODEL KEY → DISEASE LABELS (class names for each model)
# ----------------------------------------------------
DISEASE_LABELS = {
    "Cassava": CASSAVA_LABELS,          # 5 classes
    "Rice": RICE_LABELS,                # 6 classes (from your screenshot)
    "PlantVillage": PLANTVILLAGE_LABELS,  # ~38 classes

    # Lowercase aliases: the Supported Species Info page looks these up
    # using its own lowercase species keys (e.g. "rice", "cassava"), which
    # never matched the capitalized keys above - so those two crops' known
    # diseases were silently always empty on that page. Adding the
    # lowercase aliases fixes that without changing anything else.
    "cassava": CASSAVA_LABELS,
    "rice": RICE_LABELS,
    "arecanut": ARECANUT_LABELS,
    "corn": CORN_LABELS,
}

# ----------------------------------------------------
# CLASS COUNTS (useful for debugging / sanity checks)
# ----------------------------------------------------
SPECIES_NUM_CLASSES = {
    "Cassava": len(CASSAVA_LABELS),
    "Rice": len(RICE_LABELS),
    "PlantVillage": len(PLANTVILLAGE_LABELS),
}
