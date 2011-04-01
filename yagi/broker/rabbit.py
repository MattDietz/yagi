import carrot.connection
import carrot.messaging

from yagi import config as conf
import yagi.log

LOG = yagi.log.logger


class Broker(object):
    def __init__(self):
        self.conn = carrot.connection.BrokerConnection(
                hostname=conf.get('rabbit_broker', 'host'),
                port=5672,
                userid=conf.get('rabbit_broker', 'user'),
                password=conf.get('rabbit_broker', 'password'),
                virtual_host=conf.get('rabbit_broker', 'vhost'))
        self.consumer = carrot.messaging.Consumer(
                connection=self.conn,
                exchange=conf.get('rabbit_broker', 'exchange'),
                routing_key=conf.get('rabbit_broker', 'routing_key'),
                queue=conf.get('rabbit_broker', 'event_topic'))

    def register_callback(self, fun):
        self.consumer.register_callback(fun)

    def loop(self):
        LOG.debug('Starting Carrot message loop')
        self.consumer.wait()
