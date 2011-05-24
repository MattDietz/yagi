import multiprocessing
import time

import yagi.config
import yagi.log
import yagi.notifier.api
import yagi.persistence
import yagi.utils

LOG = yagi.log.logger

with yagi.config.defaults_for('event_worker') as default:
    default('pidfile', 'yagi_event_worker.pid')
    default('daemonize', 'False')
    default('event_driver','yagi.broker.rabbit.Broker')

class BadMessageFormatException(Exception):
    pass

event_attributes = ['message_id', 'publisher_id', 'event_type', 'priority',
                    'payload', 'timestamp']


class EventWorker(object):
    def __init__(self):
        self.broker = yagi.utils.import_class(yagi.config.get('event_worker',
                'event_driver'))()
        self.db = yagi.persistence.persistence_driver()
        self.processes = []

    def fetched_message(self, messages):
        for message in messages:
            try:
                event_type = self.persist_event(message)
            except Exception, e:
                LOG.debug('Error processing event body', exc_info=True)
        yagi.notifier.api.notify(messages)

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
        self.db.create(event_type, m_id, message_body)
        LOG.debug('New notification created')
        return event_type

    def notifier(self):
        while True:
            time.sleep(2)
        
    def start(self):
        LOG.debug('Starting eventworker...')
        self.broker.register_callback(self.fetched_message)
        self.processes.append(multiprocessing.Process(
                target=self.broker.loop))
        #self.processes.append(multiprocessing.Process(target=self.notifier))
        for proc in self.processes:
            proc.start()

    def wait_for_finish(self):
        for proc in self.processes:
            try:
                proc.join()
            except Exception, e:
                pass


def start():
    event_worker = EventWorker()
    event_worker.start()
    event_worker.wait_for_finish()
