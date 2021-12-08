import sys
from pathlib import Path

# Directories
BASE_DIR = Path.home()
ML_DIR = Path(BASE_DIR, "machine_learning")
PROJECT_DIR = Path(ML_DIR, "projects")
TOP_DIR = Path(PROJECT_DIR, "fastfantasy")
FASTFANTASY_DIR = Path(TOP_DIR, "fastfantasy")

CONFIG_DIR = Path(FASTFANTASY_DIR, "config")
DATA_DIR = Path(FASTFANTASY_DIR, "data")

RAW_DATA_DIR = Path(DATA_DIR, "raw")
PROCESSED_DATA_DIR = Path(DATA_DIR, "processed")