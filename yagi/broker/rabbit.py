import carrot.connection
import carrot.messaging

from yagi import config as conf
import yagi.log

LOG = yagi.log.logger

WARN = 'WARN'
INFO = 'INFO'
ERROR = 'ERROR'
CRITICAL = 'CRITICAL'
DEBUG = 'DEBUG'

log_levels = (CRITICAL, ERROR, INFO, WARN, DEBUG)

class Broker(object):
    def __init__(self):
        self.conn = carrot.connection.BrokerConnection(
                hostname=conf.get('rabbit_broker', 'host'),
                port=5672,
                userid=conf.get('rabbit_broker', 'user'),
                password=conf.get('rabbit_broker', 'password'),
                virtual_host=conf.get('rabbit_broker', 'vhost'))
        self.consumers = {}
        for level in log_levels:
            self.consumers[level] = carrot.messaging.Consumer(
                connection=self.conn,
                warn_if_exists=True,
                auto_declare=False,
                exchange=conf.get('rabbit_broker', 'exchange'),
                exchange_type='topic',
                routing_key = '%s.%s' % (conf.get('rabbit_broker',
                                                  'routing_key'),
                                                  level.lower()),
                queue = '%s.%s' % (conf.get('rabbit_broker',
                                            'event_topic'),
                                            level.lower()),
                durable=conf.get_bool('rabbit_broker', 'durable'))

    def register_callback(self, fun):
        for level in log_levels:
            self.consumers[level].register_callback(fun)

    def loop(self):
        LOG.debug('Starting Carrot message loop')
        self.consumer.wait()
