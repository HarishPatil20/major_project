from pathlib import Path

src = Path(r"C:\CropProject\app\rice_detection\RiceLeafAnnotatedDataset")
dst = Path(r"C:\CropProject\app\rice_detection\RiceDetectionClean")

for split in ["train", "valid", "test"]:
    label_src = src / split / "labels"
    image_src = src / split / "images"

    label_dst = dst / split / "labels"
    image_dst = dst / split / "images"

    label_dst.mkdir(parents=True, exist_ok=True)
    image_dst.mkdir(parents=True, exist_ok=True)

    # Copy images
    for img in image_src.iterdir():
        if img.is_file():
            target = image_dst / img.name
            if not target.exists():
                target.write_bytes(img.read_bytes())

    converted = 0
    kept = 0

    for label_file in label_src.glob("*.txt"):
        output = []

        for line in label_file.read_text().splitlines():
            parts = line.split()
            if not parts:
                continue

            cls = parts[0]
            coords = list(map(float, parts[1:]))

            # Already YOLO bounding box
            if len(coords) == 4:
                output.append(line)
                kept += 1

            # Polygon -> bounding box
            elif len(coords) >= 6 and len(coords) % 2 == 0:
                xs = coords[0::2]
                ys = coords[1::2]

                xmin = max(0.0, min(xs))
                xmax = min(1.0, max(xs))
                ymin = max(0.0, min(ys))
                ymax = min(1.0, max(ys))

                xc = (xmin + xmax) / 2
                yc = (ymin + ymax) / 2
                w = xmax - xmin
                h = ymax - ymin

                output.append(
                    f"{cls} {xc:.8f} {yc:.8f} {w:.8f} {h:.8f}"
                )
                converted += 1

        (label_dst / label_file.name).write_text(
            "\n".join(output) + ("\n" if output else "")
        )

    print(f"{split}: converted={converted}, existing_bbox={kept}")

print("\nDONE: RiceDetectionClean created.")
