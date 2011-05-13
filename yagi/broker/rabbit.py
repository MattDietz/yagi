import carrot.connection
import carrot.messaging

from yagi import config as conf
import yagi.log

LOG = yagi.log.logger


class Broker(object):
    def __init__(self):
        config = conf.config_with('rabbit_broker')
        self.conn = carrot.connection.BrokerConnection(
                hostname=config('host'),
                port=5672,
                userid=config('user'),
                password=config('password'),
                virtual_host=config('vhost'))
        self.consumer = carrot.messaging.Consumer(
                connection=self.conn,
                exchange=config('exchange'),
                exchange_type=config('exchange_type'),
                routing_key=config('routing_key'),
                queue=config('event_topic'),
                durable=conf.get_bool('rabbit_broker', 'durable'))

    def register_callback(self, fun):
        self.consumer.register_callback(fun)

    def loop(self):
        LOG.debug('Starting Carrot message loop')
        self.consumer.wait()
