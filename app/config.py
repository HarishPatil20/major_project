from pathlib import Path
import torch

# Project root is assumed to be the directory that contains src/, data/, models/, etc.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_RAW_DIR = DATA_DIR / "raw"

MODELS_DIR = PROJECT_ROOT / "models"

EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
