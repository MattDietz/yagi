import logging

import yagi.config

logger = logging

with yagi.config.defaults_for('logging') as default:
    default('logfile', 'yagi.log')
    default('default_level', 'DEBUG')
    default('logger', 'logging')


class YagiLogger(logging.Logger):
    def __init__(self, name, level=None):
        logging.Logger.__init__(self, name, logging.DEBUG)
        handlers = []
        handlers.append(logging.StreamHandler())
        logfile = yagi.config.get('logging', 'logfile')
        if logfile:
            handlers.append(logging.FileHandler(
                            filename=logfile))
        for handler in handlers:
            logging.Logger.addHandler(self, handler)


def setup_logging():
    logging.root = YagiLogger("YagiLogger")
    logging.setLoggerClass(YagiLogger)
