try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

SYSTEM_PROMPT = """
You are CropDoctor AI, a local agriculture assistant.

Answer only questions about:
- crops and plant diseases
- symptoms and prevention
- pest management
- irrigation
- fertilizers
- farming practices

Use simple English.
Give short, practical answers useful for farmers.
Do not claim to provide live or current information.
If the question is unrelated to agriculture, politely say you only answer agriculture-related questions.
"""

# ==========================================================
# OFFLINE, KEYWORD-AWARE FALLBACK
# ==========================================================
# Used only when a local LLM via Ollama isn't available (package not
# installed, server not running, or model not pulled). Previously this
# returned one fixed block of text no matter what was asked — so "red
# soil" and "how do I treat blast" got the identical generic answer.
# This version actually reads the prompt and responds to what's in it,
# so the assistant is genuinely useful even without Ollama configured.

_SOIL_INFO = {
    "red soil": (
        "Red soil is iron-rich and porous, usually low in nitrogen, phosphorus and "
        "organic matter. Add well-rotted farmyard manure/compost, apply a "
        "phosphorus-rich fertilizer (SSP/DAP), and add lime if it tests acidic. "
        "Millets, groundnut, pulses, cotton and arecanut generally do well on red "
        "soil with proper irrigation."
    ),
    "black soil": (
        "Black (cotton) soil holds moisture well and is rich in calcium, potassium "
        "and magnesium, but often low in nitrogen and phosphorus. Good for cotton, "
        "soybean and wheat — ensure drainage since it can waterlog, and supplement "
        "nitrogen and phosphorus fertilizer."
    ),
    "clay soil": (
        "Clay soil retains water and nutrients well but drains slowly and can "
        "compact easily. Improve drainage with raised beds or added organic "
        "matter, avoid working it while wet, and favor crops tolerant of heavier "
        "soils such as rice or leafy vegetables."
    ),
    "sandy soil": (
        "Sandy soil drains fast and loses nutrients quickly. Irrigate more "
        "frequently in smaller amounts, add organic compost to improve water and "
        "nutrient retention, and split fertilizer doses instead of one large "
        "application."
    ),
    "loamy soil": (
        "Loamy soil is well-balanced for most crops, with good drainage and "
        "nutrient retention. Maintain organic matter with regular compost/FYM and "
        "rotate crops to preserve fertility."
    ),
    "alluvial soil": (
        "Alluvial soil is fertile and well-suited to rice, wheat, sugarcane and "
        "most cereals. Keep NPK application balanced and manage irrigation "
        "carefully to avoid waterlogging during monsoon."
    ),
}

_TOPIC_INFO = [
    (
        ["pest", "insect", "bug", "hispa", "borer", "aphid"],
        "Pest control: inspect the crop weekly, remove and destroy visibly "
        "infested leaves or parts, and use neem oil or a recommended "
        "insecticide (e.g. Chlorpyrifos) at the first sign of an outbreak "
        "rather than waiting.",
    ),
    (
        ["fertilizer", "npk", "nutrient", "manure", "compost"],
        "Fertilizer guidance: apply balanced NPK based on the crop's growth "
        "stage — more nitrogen early for vegetative growth, more phosphorus "
        "and potassium during flowering and fruiting — and add organic "
        "manure or compost to improve long-term soil health.",
    ),
    (
        ["irrigation", "water", "drought", "rain", "moisture"],
        "Irrigation advice: water early morning or evening to reduce "
        "evaporation loss, avoid waterlogging (especially on heavier "
        "soils), and adjust frequency to soil type — sandy soils need "
        "lighter, more frequent watering than clay soils.",
    ),
    (
        ["blight", "blast", "rust", "spot", "mildew", "rot", "disease", "fungus", "fungal", "wilt"],
        "Disease management: remove and destroy visibly infected leaves, "
        "avoid overhead watering late in the day (fungal disease spreads in "
        "prolonged leaf wetness), and apply a suitable fungicide such as "
        "Mancozeb or Propiconazole at the first sign of spotting.",
    ),
    (
        ["weather", "forecast", "monsoon", "season", "climate"],
        "Weather planning: check the Weather page for your local forecast "
        "before spraying (avoid spraying just before rain), and time "
        "sowing or harvesting around expected dry spells where possible.",
    ),
]


def _offline_advice(prompt: str) -> str:
    lowered = (prompt or "").lower()
    lines = []

    for soil_key, soil_text in _SOIL_INFO.items():
        if soil_key in lowered:
            lines.append(f"**{soil_key.title()}:** {soil_text}")

    for keywords, text in _TOPIC_INFO:
        if any(word in lowered for word in keywords):
            lines.append(text)

    if not lines:
        lines.append(
            "Ensure proper field drainage, apply balanced NPK nutrients for "
            "your crop's growth stage, inspect leaves regularly for early "
            "signs of pests or disease, and irrigate according to your soil "
            "type."
        )

    body = "\n\n".join(f"• {line}" for line in lines)

    return (
        "🤖 **CropDoctor AI Advisory:**\n\n"
        f"{body}\n\n"
        "*(Offline rule-based guidance — install and run Ollama locally "
        "(`pip install ollama` and `ollama pull llama3.2:1b`) for fully "
        "conversational AI responses.)*"
    )


def run_llm(prompt):
    if OLLAMA_AVAILABLE:
        try:
            response = ollama.chat(
                model="llama3.2:1b",
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response["message"]["content"]

        except Exception:
            # Package installed but the Ollama server isn't running, isn't
            # reachable, or the model hasn't been pulled yet — fall back to
            # the offline advisory below instead of a raw error.
            pass

    return _offline_advice(prompt)
