from loguru import logger

def log_exception(logger, level, message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log(level, f"Exception in {func.__name__}: {e}, {message}")
                raise
        return wrapper
    return decorator

import datetime

now = datetime.datetime.now()
filename = now.strftime("logs/Stitch_%Y-%m-%d_%H-%M-%S") + ".log"
logger.add(
    filename,
    rotation="10 MB",
    backtrace=True,
    format="{time}, {level}, {message}"
)

logger.info("Start Event Send Server")