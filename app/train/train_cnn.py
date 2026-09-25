import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torchvision.models import ResNet18_Weights
from torch.utils.data import DataLoader

# Dataset path
DATASET_PATH = "dataset/PlantVillage"
MODEL_PATH = "models/plant_village_best.pth"

# Create models folder
os.makedirs("models", exist_ok=True)

# Image transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# Load dataset
dataset = datasets.ImageFolder(DATASET_PATH, transform=transform)

print("Classes:", dataset.classes)
print("Total Images:", len(dataset))

# Data Loader
train_loader = DataLoader(
    dataset,
    batch_size=16,
    shuffle=True,
    num_workers=0
)

# Pretrained CNN Model
model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, len(dataset.classes))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using:", device)

model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

epochs = 2

for epoch in range(epochs):
    model.train()
    running_loss = 0.0

    for batch_idx, (images, labels) in enumerate(train_loader):

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item()

        if batch_idx % 100 == 0:
            print(f"Epoch {epoch+1}/{epochs} | Batch {batch_idx}/{len(train_loader)}")

    print(f"Epoch {epoch+1} Completed | Loss: {running_loss:.4f}")

torch.save(model.state_dict(), MODEL_PATH)

print("===================================")
print("Training Completed Successfully")
print("Model Saved:", MODEL_PATH)
print("===================================")