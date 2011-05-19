import ConfigParser
import functools
import os
import sys

import yagi.log

LOG = yagi.log.logger

CONFIG_FILE = 'yagi.conf'
CONFIG_PATHS = ['./', '/etc/']

config = None
config_path = None

def setup(**kwargs):
    if kwargs['config_path']:
        parse_conf(kwargs['config_path'])

def parse_conf(path=None):
    global config, config_path
    config_path = path
    config = ConfigParser.ConfigParser()
    if not config_path:
        for path in CONFIG_PATHS:
            path = path + CONFIG_FILE
            if os.path.exists(path):
                config_path = path
                break
    else:
        if not os.path.exists(path):
            raise Exception, "No configuration '%s' found" % path
    config.read(config_path)
    return config


def lazy_load_config(fun):
    def decorate(*args, **kwargs):
        global config
        if not config:
            config = parse_conf()
        try:
            return fun(*args, **kwargs)
        except ConfigParser.NoOptionError, e:
            LOG.warn(e)
            return kwargs.get('default', None)
    return decorate


@lazy_load_config
def get(*args, **kwargs):
    return config.get(*args)


@lazy_load_config
def get_bool(*args, **kwargs):
    var = config.get(*args)
    if var.lower() == 'true':
        return True
    return False


def config_with(*args):
    return functools.partial(get, *args)
