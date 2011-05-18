import ConfigParser
import functools
import os

import yagi.log

LOG = yagi.log.logger

CONFIG_FILE = 'yagi.conf'
CONFIG_PATHS = ['./', '/etc/']

config = None


def parse_conf():
    config = None
    for path in CONFIG_PATHS:
        path = path + CONFIG_FILE
        if os.path.exists(path):
            config = ConfigParser.ConfigParser()
            config.read(path)
            break
    return config


def lazy_load_config():
    def decorate(f):
        global config
        if not config:
            config = parse_conf()

        def returns_default(*args, **kwargs):
            try:
                return f(*args)
            except ConfigParser.NoOptionError, e:
                LOG.warn(e)
                return kwargs.get('default', None)
        return returns_default
    return decorate


@lazy_load_config()
def get(*args, **kwargs):
    return config.get(*args)


@lazy_load_config()
def get_bool(*args, **kwargs):
    var = config.get(*args)
    if var.lower() == 'true':
        return True
    return False


def config_with(*args):
    return functools.partial(get, *args)
