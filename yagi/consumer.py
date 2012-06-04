import yagi.config
import yagi.log
import yagi.utils

LOG = yagi.log.logger


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
                prev_app = yagi.utils.import_class(a)(prev_app,
                                                      queue_name=self.queue_name)
            self.app = prev_app

    def max_messages(self):
        return int(self.config('max_messages'))

    def connect(self, connection, consumer):
        self.connection = connection
        self.consumer = consumer

    def fetched_messages(self, messages):
        try:
            self.app(messages)
        except Exception, e:
            LOG.exception("Error in fetched_messages: \n%s" % e)
