import json

import yagi.config
import yagi.log
import yagi.notifier
import yagi.persistence
import yagi.utils

LOG = yagi.log.logger


class EventWorker(object):
    def __init__(self):
        self.broker = yagi.utils.import_class(yagi.config.get('event_worker',
                'event_driver'))()
        self.db = yagi.persistence.persistence_driver()

    def fetched_message(self, message_data, message):
        LOG.debug('Received %s' % (message_data))
        try:
            obj = json.loads(message_data)
            self.db.create(obj['key'], json.dumps(obj['content']))
            LOG.debug('New notification created')
            yagi.notifier.notify(yagi.utils.topic_url(obj['key']))
        except Exception, e:
            LOG.debug(e)
        finally:
            message.ack()

    def start(self):
        LOG.debug('Starting eventworker...')
        self.broker.register_callback(self.fetched_message)
        self.broker.loop()


def start():
    event_worker = EventWorker()
    event_worker.start()
