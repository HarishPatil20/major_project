def clean_label(label: str) -> str:
    # Remove triple underscores
    label = label.replace("___", "_")

    # Replace underscores with spaces
    label = label.replace("_", " ")

    # Split species and disease if present
    if " " in label:
        label = label.replace("(", "").replace(")", "")

    # Capitalize each word
    return " ".join([w.capitalize() for w in label.split()])
