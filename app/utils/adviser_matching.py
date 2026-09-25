from auth.database import get_advisers


def _tokens(value):
    return {
        token.strip().lower()
        for token in str(value or "").replace("/", ",").split(",")
        if token.strip()
    }


def get_adviser_recommendations(crop, disease, limit=3):
    crop_tokens = _tokens(crop)
    disease_tokens = _tokens(disease)
    matches = []

    for adviser in get_advisers():
        adviser_crops = _tokens(adviser["crops"])
        adviser_diseases = _tokens(adviser["diseases"])
        crop_match = bool(crop_tokens & adviser_crops)
        disease_match = bool(disease_tokens & adviser_diseases)
        if crop_match or disease_match:
            score = int(crop_match) + int(disease_match)
            matches.append((score, adviser))

    matches.sort(key=lambda item: (-item[0], item[1]["full_name"].lower()))
    return [adviser for _, adviser in matches[:limit]]
