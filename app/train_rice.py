from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from PIL import Image
from torchvision.transforms.functional import pil_to_tensor


# ==========================================================
# PATHS
# ==========================================================

ROOT = Path(r"C:\CropProject\app\rice_detection\RiceDetectionClean")
MODEL_DIR = Path(r"C:\CropProject\app\models")

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# RICE DATASET
# ==========================================================

class RiceDataset(Dataset):

    def __init__(self, root, split):

        self.root = Path(root)
        self.image_dir = self.root / split / "images"
        self.label_dir = self.root / split / "labels"

        self.samples = []

        for image_path in sorted(self.image_dir.iterdir()):

            if image_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                continue

            label_path = self.label_dir / (image_path.stem + ".txt")

            if not label_path.exists():
                continue

            # Check that at least one valid box exists
            valid_box_found = False

            for line in label_path.read_text().splitlines():

                parts = line.split()

                if len(parts) != 5:
                    continue

                try:
                    class_id = int(parts[0])
                    xc, yc, w, h = map(float, parts[1:])

                    if (
                        0 <= class_id < 8
                        and w > 0
                        and h > 0
                        and 0 <= xc <= 1
                        and 0 <= yc <= 1
                    ):
                        valid_box_found = True
                        break

                except ValueError:
                    continue

            if valid_box_found:
                self.samples.append((image_path, label_path))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):

        image_path, label_path = self.samples[index]

        image = Image.open(image_path).convert("RGB")

        width, height = image.size

        boxes = []
        labels = []

        for line in label_path.read_text().splitlines():

            parts = line.split()

            if len(parts) != 5:
                continue

            try:

                class_id = int(parts[0])
                xc, yc, w, h = map(float, parts[1:])

            except ValueError:
                continue

            if not (
                0 <= class_id < 8
                and w > 0
                and h > 0
                and 0 <= xc <= 1
                and 0 <= yc <= 1
            ):
                continue

            xmin = (xc - w / 2) * width
            ymin = (yc - h / 2) * height
            xmax = (xc + w / 2) * width
            ymax = (yc + h / 2) * height

            xmin = max(0, min(xmin, width))
            ymin = max(0, min(ymin, height))
            xmax = max(0, min(xmax, width))
            ymax = max(0, min(ymax, height))

            if xmax > xmin and ymax > ymin:

                boxes.append([
                    xmin,
                    ymin,
                    xmax,
                    ymax
                ])

                # 0 = background
                # Rice classes = 1 to 8
                labels.append(class_id + 1)

        # Guaranteed [N,4] tensor
        if boxes:
            boxes_tensor = torch.tensor(
                boxes,
                dtype=torch.float32
            )
            labels_tensor = torch.tensor(
                labels,
                dtype=torch.int64
            )
        else:
            boxes_tensor = torch.zeros(
                (0, 4),
                dtype=torch.float32
            )
            labels_tensor = torch.zeros(
                (0,),
                dtype=torch.int64
            )

        image_tensor = pil_to_tensor(image).float() / 255.0

        target = {
            "boxes": boxes_tensor,
            "labels": labels_tensor,
            "image_id": torch.tensor(
                [index],
                dtype=torch.int64
            )
        }

        return image_tensor, target


# ==========================================================
# COLLATE FUNCTION
# ==========================================================

def collate_fn(batch):
    return tuple(zip(*batch))


# ==========================================================
# DATASET
# ==========================================================

train_dataset = RiceDataset(
    ROOT,
    "train"
)

train_loader = DataLoader(
    train_dataset,
    batch_size=2,
    shuffle=True,
    num_workers=0,
    collate_fn=collate_fn
)

print("======================================")
print("Rice Dataset Loaded")
print("Training images:", len(train_dataset))
print("======================================")


# ==========================================================
# DEVICE
# ==========================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)


# ==========================================================
# FASTER R-CNN
# ==========================================================

model = fasterrcnn_resnet50_fpn(
    weights=None,
    num_classes=9
)

model.to(device)

print("Faster R-CNN configured")
print("Number of classes: 9")


# ==========================================================
# OPTIMIZER
# ==========================================================

optimizer = torch.optim.SGD(
    model.parameters(),
    lr=0.005,
    momentum=0.9,
    weight_decay=0.0005
)


# ==========================================================
# TRAINING
# ==========================================================

EPOCHS = 10

for epoch in range(EPOCHS):

    model.train()

    total_loss = 0.0

    print()
    print("======================================")
    print(f"Epoch {epoch + 1}/{EPOCHS}")
    print("======================================")

    for batch_index, (images, targets) in enumerate(train_loader):

        images = [
            image.to(device)
            for image in images
        ]

        targets = [
            {
                key: value.to(device)
                for key, value in target.items()
            }
            for target in targets
        ]

        # Skip unexpected empty targets
        if any(
            target["boxes"].shape[0] == 0
            for target in targets
        ):
            continue

        loss_dict = model(
            images,
            targets
        )

        loss = sum(loss_dict.values())

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

        if (batch_index + 1) % 50 == 0:

            print(
                f"Batch {batch_index + 1}/{len(train_loader)} "
                f"| Loss: {loss.item():.4f}"
            )

    average_loss = (
        total_loss / len(train_loader)
    )

    print(
        f"Epoch {epoch + 1} completed "
        f"| Average Loss: {average_loss:.4f}"
    )

    # ======================================================
    # CHECKPOINT
    # ======================================================

    checkpoint_path = (
        MODEL_DIR /
        f"rice_fasterrcnn_epoch_{epoch + 1}.pth"
    )

    torch.save(
        model.state_dict(),
        checkpoint_path
    )

    print(
        "Checkpoint saved:",
        checkpoint_path
    )


# ==========================================================
# FINAL MODEL
# ==========================================================

final_model = (
    MODEL_DIR /
    "rice_fasterrcnn.pth"
)

torch.save(
    model.state_dict(),
    final_model
)

print()
print("======================================")
print("Rice Faster R-CNN training completed!")
print("Final model:")
print(final_model)
print("======================================")