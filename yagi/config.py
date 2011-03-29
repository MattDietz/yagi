import ConfigParser

DEFAULT_CONF_PATH='yagi.conf'

config = None

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
        return var
    except Exception, e:
        return kwargs.get('default', None)
