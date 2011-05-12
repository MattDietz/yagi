import ConfigParser

import yagi.log

LOG = yagi.log.logger

DEFAULT_CONF_PATH = 'yagi.conf'

config = None
argv = None


def parse_conf(conf_path=None):
    if not conf_path:
        conf_path = DEFAULT_CONF_PATH
    config = ConfigParser.ConfigParser()
    config.read(conf_path)
    return config


def get(*args, **kwargs):
    global config
    if not config:
        config = parse_conf()
    try:
        var = config.get(*args)
    except Exception, e:
        LOG.warn(e)
        return kwargs.get('default', None)
    return var

def get_bool(*args, **kwargs):
    global config
    if not config:
        config = parse_conf()
    try:
        var = config.get(*args)
        if var.lower() == 'true':
            return True
        return False
    except Exception, e:
        LOG.warn(e)
        return kwargs.get('default', None)

def setup(sys_argv):
    global argv
    global config
    argv = sys_argv
    config = parse_conf()
