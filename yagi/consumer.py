import yagi.config
import yagi.log
import yagi.utils


class Consumer(object):
    def __init__(self, queue_name, app=None, config=None):
        self.queue_name = queue_name
        if config:
            self.config = config.get
        else:
            self.config = yagi.config.config_with('consumer:%s' % queue_name)
        if app:
            self.app = app
        else:
            apps = [a.strip() for a in self.config('apps').split(',')]
            prev_app = None
            for a in apps:
                prev_app = yagi.utils.import_class(a)(prev_app)
            self.app = prev_app

    def fetched_messages(self, messages):
        self.app(messages)
