import os
from pathlib import Path

BASE = os.path.dirname(os.path.realpath(__file__))

DATA = Path(BASE, "data")
TOURNAMENT_DATA = Path(DATA, "tournaments")
RAW_TOURNAMENTS = Path(TOURNAMENT_DATA, "raw")
PROCESSED_TOURNAMENTS = Path(TOURNAMENT_DATA, "processed")

DATA_RAW = Path(DATA, "raw")
DATA_PROCESSED = Path(DATA, "processed")


