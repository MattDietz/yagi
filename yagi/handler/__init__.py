import yagi.config
import yagi.log

LOG = yagi.log.logger


class BaseHandler(object):
    def __init__(self, app=None):
        self.app = app

    def __call__(self, messages):
        """
        if self.app:
            result = self.app(*args, **kwargs)
        return result
        """
        raise NotImplementedError()
