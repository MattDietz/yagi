import functools
import os
import sys

from contextlib import contextmanager
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError

import yagi.filters

CONFIG_FILE = 'yagi.conf'
CONFIG_PATHS = ['./', '/etc/']

config = None
config_path = None
config_defaults = {'global': {'verbose': 'True',
                               'debug': 'False'},
                    # Defining defaults for this here, as it's usage is spread
                    # out all over the code. -mdragon.
                    'event_feed': {'pidfile': 'yagi_feed.pid',
                                   'daemonize': 'False',
                                   'port': 8080,
                                   'serializer_driver': 'yagi.serializer.atom',
                                   'feed_title': 'Notifications'}}

filters = {}


class DefaultConfigParser(SafeConfigParser):

    def get(self, section, option, raw=False, vars=None):
        try:
            return SafeConfigParser.get(self, section, option, raw, vars)
        except NoSectionError:
            try:
                section_defaults = config_defaults[section]
            except KeyError:
                raise NoSectionError(section)
            try:
                return section_defaults[option]
            except KeyError:
                raise NoOptionError(option, section)
        except NoOptionError:
            try:
                section_defaults = config_defaults[section]
                return section_defaults[option]
            except KeyError:
                raise NoOptionError(option, section)


def setup(**kwargs):
    if kwargs['config_path']:
        parse_conf(kwargs['config_path'])


def parse_conf(path=None):
    global config, config_path
    config_path = path
    config = DefaultConfigParser()
    if not config_path:
        for path in CONFIG_PATHS:
            path = path + CONFIG_FILE
            if os.path.exists(path):
                config_path = path
                break
    else:
        if not os.path.exists(path):
            raise Exception("No configuration '%s' found" % path)
    if config_path:
        config.read(config_path)
    return config


def get_filter(filter_name):
    if config.has_section("filter:%s" % filter_name):
        section = config_with("filter:%s" % filter_name)
        map_file = section("map_file")
        return  yagi.filters.FilterMessage(map_file)
    raise Exception("No filter named %s" % filter_name)


def defaults(section, option, value):
    section_defaults = config_defaults.get(section) or dict()
    section_defaults[option] = str(value)
    config_defaults[section] = section_defaults


@contextmanager
def defaults_for(section):
    yield functools.partial(defaults, section)


def lazy_load_config(fun):
    def decorate(*args, **kwargs):
        import yagi.log
        LOG = yagi.log.logger
        global config
        if not config:
            config = parse_conf()
        try:
            return fun(*args, **kwargs)
        except NoOptionError, e:
            LOG.debug(e)
            return kwargs.get('default', None)
    return decorate


@lazy_load_config
def get(*args, **kwargs):
    return config.get(*args)


@lazy_load_config
def get_bool(*args, **kwargs):
    return config.getboolean(*args)


def config_with(*args):
    return functools.partial(get, *args)
