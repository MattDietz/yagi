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
        config = conf.config_with('rabbit_broker')
        self.conn = carrot.connection.BrokerConnection(
                hostname=config('host'),
                port=5672,
                userid=config('user'),
                password=config('password'),
                virtual_host=config('vhost'))
        self.consumers = {}
        for level in log_levels:
            self.consumers[level] = carrot.messaging.Consumer(
                connection=self.conn,
                warn_if_exists=True,
                exchange=config('exchange'),
                exchange_type=config('exchange_type'),
                routing_key = '%s.%s' % (config('routing_key'),
                                                level.lower()),
                queue = '%s.%s' % (config('event_topic'),
                                          level.lower()),
                routing_key=config('routing_key'),
                queue=config('event_topic'),
                durable=conf.get_bool('rabbit_broker', 'durable'))

    def register_callback(self, fun):
        for level in log_levels:
            self.consumers[level].register_callback(fun)

    def loop(self):
        LOG.debug('Starting Carrot message loop')
        self.consumer.wait()
