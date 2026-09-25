from pathlib import Path
from typing import Union

import torch
import torch.nn as nn
from torchvision import models

from config import DEVICE
from utils.species_mapping import (
    DISEASE_MODEL_PATHS,
    DISEASE_LABELS,
)

PathLike = Union[str, Path]


# ============================================================
# BUILD RESNET18 MODEL
# ============================================================
def _build_resnet18(num_classes: int):
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


# ============================================================
# LOAD RESNET18 MODEL
# ============================================================
def load_resnet_model(weights_path: PathLike, num_classes: int):
    model = _build_resnet18(num_classes)

    state_dict = torch.load(weights_path, map_location=DEVICE)

    model.load_state_dict(state_dict)

    model.to(DEVICE)
    model.eval()

    return model


# ============================================================
# SPECIES MODEL
# ============================================================
def load_species_model(device="cpu"):
    # Species model not used
    return None


# ============================================================
# LOAD DISEASE MODEL
# ============================================================
def load_disease_model(model_path: PathLike, device=DEVICE):

    model_path = str(model_path)

    model_key = None

    for key, path in DISEASE_MODEL_PATHS.items():
        if str(path) == model_path:
            model_key = key
            break

    if model_key is None:
        model_key = "PlantVillage"

    num_classes = len(DISEASE_LABELS[model_key])

    model = load_resnet_model(model_path, num_classes)

    model.to(device)
    model.eval()

    return model