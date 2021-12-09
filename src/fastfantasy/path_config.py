import os
from pathlib import Path

BASE = os.path.dirname(os.path.realpath(__file__))

DATA = Path(BASE, "data")
DATA_RAW = Path(DATA, "raw")
DATA_PROCESSED = Path(DATA, "processed")


