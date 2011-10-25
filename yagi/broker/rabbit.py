import json
import socket
import time

import carrot.connection
import carrot.messaging

from yagi import config as conf
import yagi.log

with conf.defaults_for('rabbit_broker') as default:
    default('host', 'localhost')
    default('user', 'guest')
    default('password', 'guest')
    default('port', 5672)
    default('vhost', '/')
    default('poll_delay', 1)
    default('reconnect_delay', 5)
    default('connection_retry_attempts', 3)

LOG = yagi.log.logger


class Broker(object):
    def __init__(self):
        self.consumers = []

    def add_consumer(self, consumer):
        self.establish_consumer_connection(consumer)
        self.consumers.append(consumer)

    def establish_consumer_connection(self, consumer):
        # for now all consumers use the same queue connection
        # That may not be the case forever
        config = conf.config_with('rabbit_broker')

        # try a few times to connect, we might have lost the connection
        for i in xrange(int(config('connection_retry_attempts'))):
            try:
                connection = carrot.connection.BrokerConnection(
                                hostname=config('host'),
                                port=config('port'),
                                userid=config('user'),
                                password=config('password'),
                                virtual_host=config('vhost'))
                carrot_consumer = carrot.messaging.Consumer(
                        connection=connection,
                        warn_if_exists=True,
                        exchange=consumer.config('exchange'),
                        exchange_type=consumer.config('exchange_type'),
                        routing_key=consumer.config('routing_key'),
                        queue=consumer.queue_name,
                        durable=consumer.config('durable') == 'True' or False)
                consumer.connect(connection, carrot_consumer)
                return
            except socket.error, e:
                delay = int(config('reconnect_delay')) * i
                time.sleep(delay)
        raise Exception("Could not re-establish connection to rabbit! :-(")

    def loop(self):
        poll_delay = float(conf.get('rabbit_broker', 'poll_delay'))
        while True:
            try:
                for consumer in self.consumers:
                    messages = []
                    for n in xrange(consumer.max_messages()):
                        msg = consumer.consumer.fetch(enable_callbacks=False)
                        if not msg:
                            break
                        try:
                            LOG.info('Received message on queue %s' %
                                consumer.queue_name)
                            messages.append(msg.payload)
                        except Exception, e:
                            LOG.error('Message decoding failed!')
                            continue
                        if not msg.acknowledged:
                            msg.ack()
                    consumer.fetched_messages(messages)
                if poll_delay:
                    time.sleep(poll_delay)
            except socket.error, e:
                LOG.critical("Rabbit connection lost, reconnecting")
                self.establish_consumer_connection(consumer)
            except Exception, e:
                LOG.critical(e)
