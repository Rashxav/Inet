import logging
from logging.handlers import TimedRotatingFileHandler
import os


class AppLogger:
    def __init__(self, log_dir="logs", log_file="cosmos.log"):
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_file)

        self.logger = logging.getLogger("CosmosLogger")
        self.logger.setLevel(logging.INFO)

        handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=7, encoding="utf-8")
        handler.suffix = "%Y-%m-%d"

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)
