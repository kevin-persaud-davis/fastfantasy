import sys
from pathlib import Path

# Directories
BASE_DIR = Path.home()
ML_DIR = Path(BASE_DIR, "machine_learning")
PROJECT_DIR = Path(ML_DIR, "projects")
FASTFANTASY_DIR = Path(PROJECT_DIR, "fastfantasy")

CONFIG_DIR = Path(FASTFANTASY_DIR, "config")
DATA_DIR = Path(FASTFANTASY_DIR, "data")