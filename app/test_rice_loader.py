from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset

class RiceDataset(Dataset):
    def __init__(self, root, split):
        self.root = Path(root)
        self.image_dir = self.root / split / "images"
        self.label_dir = self.root / split / "labels"

        self.images = sorted([
            p for p in self.image_dir.iterdir()
            if p.suffix.lower() in [".jpg", ".jpeg", ".png"]
        ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image_path = self.images[idx]
        label_path = self.label_dir / (image_path.stem + ".txt")

        image = Image.open(image_path).convert("RGB")
        width, height = image.size

        boxes = []
        labels = []

        if label_path.exists():
            for line in label_path.read_text().splitlines():
                parts = line.split()

                if len(parts) != 5:
                    continue

                class_id = int(parts[0])
                xc, yc, w, h = map(float, parts[1:])

                xmin = (xc - w / 2) * width
                ymin = (yc - h / 2) * height
                xmax = (xc + w / 2) * width
                ymax = (yc + h / 2) * height

                xmin = max(0, min(xmin, width))
                ymin = max(0, min(ymin, height))
                xmax = max(0, min(xmax, width))
                ymax = max(0, min(ymax, height))

                if xmax > xmin and ymax > ymin:
                    boxes.append([xmin, ymin, xmax, ymax])
                    labels.append(class_id + 1)

        target = {
            "boxes": torch.tensor(boxes, dtype=torch.float32),
            "labels": torch.tensor(labels, dtype=torch.int64),
            "image_id": torch.tensor([idx])
        }

        image = torch.tensor(
            list(image.getdata()),
            dtype=torch.uint8
        ).reshape(height, width, 3).permute(2, 0, 1).float() / 255.0

        return image, target


root = r"C:\CropProject\app\rice_detection\RiceDetectionClean"

dataset = RiceDataset(root, "train")

print("Dataset loaded successfully!")
print("Total training images:", len(dataset))

image, target = dataset[0]

print("Image shape:", image.shape)
print("Number of boxes:", len(target["boxes"]))
print("Labels:", target["labels"].tolist())
print("Boxes:")
print(target["boxes"])
