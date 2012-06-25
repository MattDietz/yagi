import yagi.config
import yagi.log
import yagi.utils

LOG = yagi.log.logger


class Consumer(object):
    def __init__(self, queue_name, app=None, config=None):
        self.filters = []
        self.queue_name = queue_name
        if config:
            self.config = config.get
        else:
            self.config = yagi.config.config_with("consumer:%s" % queue_name)
        if app:
            self.app = app
        else:
            apps = [a.strip() for a in self.config("apps").split(",")]
            prev_app = None
            for a in apps:
                prev_app = yagi.utils.import_class(a)(prev_app,
                                                    queue_name=self.queue_name)
            self.app = prev_app

        filters = [f.strip() for f in self.config("filters").split(",")]
        for f in filters:
            # Get the filters from the registry
            self.filters.append(yagi.config.get_filter(f))

    def max_messages(self):
        return int(self.config("max_messages"))

    def connect(self, connection, consumer):
        self.connection = connection
        self.consumer = consumer

    def fetched_messages(self, messages):
        def next_message():
            for message in messages:
                self.message = message
                payload = message.payload
                for f in self.filters:
                    payload = f(payload)
                    print f
                    print "*"*80
                yield payload
                #message.ack()

        try:
            self.app(next_message)
        except Exception, e:
            # If we get all the way back out here, that's bad juju
            LOG.exception("Error in fetched_messages: \n%s" % e)
