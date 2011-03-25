import carrot.connection
import carrot.messaging

class Broker(object):
    def __init__(self, conf):
        self.conn = carrot.connection.BrokerConnection(
                hostname=conf.get('rabbit_broker', 'event_host'),
                port=5672,
                user=conf.get('rabbit_broker', 'user'),
                password=conf.get('rabbit_broker', 'password'),
                virtual_host=conf.get('rabbit_broker', 'vhost')
                )
        self.consumer = carrot.messaging.Consumer(
                connection=self.conn,
                queue=conf.get('rabbit_broker', 'event_topic')
                )

    def register_callback(self, fun):
        self.consumer.register_callback(fun)

    def loop(self):
        self.consumer.wait() 
