import logging

import yagi.config

logger = logging


class YagiLogger(logging.Logger):
    def __init__(self, name, level=None):
        conf = yagi.config.parse_conf()
        logging.Logger.__init__(self, name, logging.DEBUG)
        handlers = []
        handlers.append(logging.StreamHandler())
        logfile = conf.get('logging', 'logfile')
        if logfile:
            handlers.append(logging.FileHandler(
                            filename=logfile))
        for handler in handlers:
            logging.Logger.addHandler(self, handler)


def setup_logging():
    logging.root = YagiLogger("YagiLogger")


logging.setLoggerClass(YagiLogger)
