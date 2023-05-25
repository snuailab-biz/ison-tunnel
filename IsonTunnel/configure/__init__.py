
from pathlib import Path
FILE = Path(__file__).resolve()
CONFIG_ROOT = FILE.parents[0]  # YOLO

from .ison_logger import ison_logger