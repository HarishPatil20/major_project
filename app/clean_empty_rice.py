from pathlib import Path

root = Path(r"C:\CropProject\app\rice_detection\RiceDetectionClean")

removed = 0

for label_file in (root / "train" / "labels").glob("*.txt"):

    valid = [
        line for line in label_file.read_text().splitlines()
        if line.strip() and len(line.split()) == 5
    ]

    if not valid:
        stem = label_file.stem

        label_file.unlink()

        for ext in [".jpg", ".jpeg", ".png"]:
            image_file = root / "train" / "images" / (stem + ext)

            if image_file.exists():
                image_file.unlink()
                break

        removed += 1

print("Empty training samples removed:", removed)
print("Remaining training labels:",
      len(list((root / "train" / "labels").glob("*.txt"))))
print("Remaining training images:",
      len(list((root / "train" / "images").glob("*"))))
