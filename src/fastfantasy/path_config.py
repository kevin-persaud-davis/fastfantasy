import os
from pathlib import Path

BASE = os.path.dirname(os.path.realpath(__file__))

DATA = Path(BASE, "data")

DATA_RAW = Path(DATA, "raw")
RAW_TOURNAMENTS = Path(DATA_RAW, "tournaments")
DATA_PROCESSED = Path(DATA, "processed")
PROCESSED_TOURNAMENTS = Path(DATA_PROCESSED, "tournaments")

