import yagi.handler
import yagi.log
import yagi.persistence

LOG = yagi.log.logger

event_attributes = ['message_id', 'publisher_id', 'event_type', 'priority',
                    'payload', 'timestamp']

class RedisHandler(yagi.handler.BaseHandler):
    def __call__(self, messages):
        result = None
        if self.app:
            result = self.app(messages)
        self.db = yagi.persistence.persistence_driver()
        for message in messages:
            self.persist_event(message)
        return result

    def persist_event(self, message):
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
                LOG.error("Invalid Message Format, missing key %s" % key)
        event_type = message_body['event_type']
        m_id = message_body['message_id']
        self.db.create(event_type, m_id, message_body)
        LOG.debug('New notification created')
