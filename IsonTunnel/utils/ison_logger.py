
import datetime
from loguru import logger

class IsonLogger:
    def __init__(self, save_name=None):
        self.logger = logger
        now = datetime.datetime.now()
        filename = now.strftime(f"logs/{save_name}_%Y-%m-%d_%H-%M-%S") + ".log"
        self.logger.add(
            filename,
            rotation="10 MB",
            backtrace=True,
            format="{time}, {level}, {message}"
        )
    
    def info(self, text):
        self.logger.info(text)

    def warning(self, text):
        self.logger.warning(text)

    def error(self, text):
        self.logger.error(text)

    def critical(self, text):
        self.logger.critical(text)

    def log_exception(self, level, message):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.logger.log(level, f"Exception in {func.__name__}: {e}, {message}")
                    raise
            return wrapper
        return decorator

    # def debug(self, text):
    #     logger.debug("Start Event Send Server")

    # def info(self, text):
    #     logger.info("Start Event Send Server")

    # def info(self, text):
    #     logger.info("Start Event Send Server")

# IsonLogger 객체 생성
