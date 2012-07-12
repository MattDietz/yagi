from ConfigParser import NoOptionError, NoSectionError
import yagi.config
import yagi.log

LOG = yagi.log.logger


class BaseHandler(object):
    CONFIG_SECTION = "DEFAULT"

    def __init__(self, app=None, queue_name=None):
        self.app = app
        self.queue_name = queue_name

    def config_get(self, key, default=None):
        return self._config_get(yagi.config.get, key, default=default)

    def config_getbool(self, key, default=None):
        return self._config_get(yagi.config.get_bool, key, default=default)

    def _config_get(self, method, key, default=None):
        val = None
        if self.queue_name is not None:
            try:
                val = method("%s:%s" % (self.CONFIG_SECTION, self.queue_name),
                             key)
            except NoSectionError:
                pass  # nothing here, try elsewhere.
        if val is None:
            val = method(self.CONFIG_SECTION, key, default=default)
        return val

    def __call__(self, messages):
        result = None
        if self.app:
            result = self.app(messages)
        self.handle_messages(messages)
        return result

    def handle_messages(self, messages):
        raise NotImplementedError()
