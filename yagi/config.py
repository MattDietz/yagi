import ConfigParser

DEFAULT_CONF_PATH='yagi.conf'

def parse_conf(conf_path=None):
    if not conf_path:
        conf_path = DEFAULT_CONF_PATH
    config = ConfigParser.ConfigParser()
    config.read(conf_path)
    return config

