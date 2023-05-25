import loguru
import datetime

class IsonLogger(loguru):
    def __init__(self):
        now = datetime.datetime.now()
        filename = now.strftime("logs/Stitch_%Y-%m-%d_%H-%M-%S") + ".log"
        self.logger.add(
            filename,
            rotation="10 MB",
            backtrace=True,
            format="{time}, {level}, {message}"
        )

        self.logger.info("Start Event Send Server")


logger = IsonLogger()
logger.info("dsjakl")
