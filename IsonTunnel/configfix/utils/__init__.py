from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # YOLO
from .configSaver import save_config, check_variable_type