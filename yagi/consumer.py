import yagi.config
import yagi.log

class Consumer(object):
    def __init__(self, app, queue_name, config):
        self.app = app
        self.queue_name = queue_name
        if config:
            self.config = config.get
        else:
            self.config = yagi.config.config_with(queue_name)

    def fetched_messages(self, messages):
        self.app(messages)
