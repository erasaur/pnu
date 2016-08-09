import logging.config
import sys
from pnu.config import pub_config


class ConfigureLogging:

    def __init__(self):
        logging.config.fileConfig(pub_config["logging"]["location"],
                                  disable_existing_loggers=False)
        logging.getLogger('apscheduler').setLevel(logging.ERROR)
        logging.getLogger('pgoapi').setLevel(logging.ERROR)
        log = logging.getLogger('pnu')
        sys.stdout = LoggerWriter(log.debug)
        sys.stderr = LoggerWriter(log.warning)


class LoggerWriter:

    def __init__(self, level):
        self.level = level

    def write(self, message):
        # eliminate extra newlines in default sys.stdout
        if message != '\n':
            self.level(message)

    def flush(self):
        self.level(sys.stderr)
