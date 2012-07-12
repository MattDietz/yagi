import logging

import yagi.config

logger = logging

with yagi.config.defaults_for('logging') as default:
    default('logfile', 'yagi.log')
    default('default_level', 'WARN')
    default('logger', 'logging')


FORMAT = "[%(levelname)s at %(asctime)s line: %(lineno)d] "\
         "%(message)s"


class YagiLogger(logging.Logger):
    def __init__(self, name, level=None):
        formatter = logging.Formatter(FORMAT)
        logging.Logger.__init__(self, name,
            logging.getLevelName(yagi.config.get('logging', 'default_level')))
        handlers = []
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)
        logfile = yagi.config.get('logging', 'logfile')
        if logfile:
            file_handler = logging.FileHandler(filename=logfile)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        for handler in handlers:
            logging.Logger.addHandler(self, handler)


def setup_logging():
    logging.root = YagiLogger("YagiLogger")
    logging.setLoggerClass(YagiLogger)
