import yagi.log
import yagi.utils

LOG = yagi.log.logger

class EventWorker(object):
    def __init__(self, conf):
        self.broker = yagi.utils.import_class(conf.get('event_worker',
                'event_driver'))(conf)

    def fetched_message(self, message_data, message_topic):
        LOG.debug('Got message %s %s' % (message_data, message_topic))

    def start(self):
        self.broker.register_callback(self.fetched_message)
        self.broker.loop()
        
def start_worker(conf):
    event_worker = EventWorker(conf)
    event_worker.start()
