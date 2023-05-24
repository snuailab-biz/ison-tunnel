# Ultralytics YOLO 🚀, GPL-3.0 license

__version__ = '8.0.53'

from IsonAI.ultralytics.yolo.engine.model import YOLO
from IsonAI.ultralytics.yolo.utils.checks import check_yolo as checks

__all__ = '__version__', 'YOLO', 'checks'  # allow simpler import