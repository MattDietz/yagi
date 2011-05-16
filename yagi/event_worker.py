import json

import yagi.config
import yagi.log
import yagi.notifier
import yagi.persistence
import yagi.utils

LOG = yagi.log.logger


class BadMessageFormatException(Exception):
    pass

event_attributes = ['message_id', 'publisher_id', 'event_type', 'priority',
                    'payload', 'timestamp']


class EventWorker(object):
    def __init__(self):
        self.broker = yagi.utils.import_class(yagi.config.get('event_worker',
                'event_driver'))()
        self.db = yagi.persistence.persistence_driver()

    def fetched_message(self, message_body, message):
        LOG.debug('Received %s' % (message_body))
        try:
            event_type = self.persist_event(message_body)
            yagi.notifier.notify(yagi.utils.topic_url(event_type))
        except Exception, e:
            LOG.debug('Error processing event body', exc_info=True)
        finally:
            message.ack()

    def persist_event(self, message_body):
        """Stores an incoming event in the database

        Messages have the following expected attributes:

        message_id - a UUID representing the id for this notification
        publisher_id - the source worker_type.host of the message
        timestamp - the GMT timestamp the notification was sent at
        event_type - the literal type of event (ex. Instance Creation)
        priority - patterned after the enumeration of Python logging levels in
                   the set (DEBUG, WARN, INFO, ERROR, CRITICAL)
        payload - A python dictionary of attributes
        """
        for key in event_attributes:
            if not key in message_body:
                raise BadMessageFormatException(
                    "Invalid Message Format, missing key %s" % key)
        event_type = message_body['event_type']
        m_id = message_body['message_id']
        self.db.create(event_type, m_id, message_json)
        LOG.debug('New notification created')
        return event_type

    def start(self):
        LOG.debug('Starting eventworker...')
        self.broker.register_callback(self.fetched_message)
        self.broker.loop()


def start():
    event_worker = EventWorker()
    event_worker.start()
