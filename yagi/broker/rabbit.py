import json
import socket
import time

import amqplib
from carrot.connection import BrokerConnection
from carrot.messaging import Consumer

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
    default('max_wait', 600)

LOG = yagi.log.logger

def confbool(val):
    if val in ('Default', None, 'None'):
        return None
    return val == 'True' or False

class NotQuiteSoStupidConsumer(Consumer):
    """ Carrot is quite broken/braindead in a number of ways.
    The proper way we should fix this is by having Yagi use Kombu for it's
    queue reading, however, until we have that done, this shim class fixes
    some of the carrot consumer class's brokenness.

    To be specific: Both queues and exchanges can be declared as durable
    and/or auto_delete (or not), *separately*. Carrot uses the same setting
    for declaring both queues and exchange. THus if your queue is durable,
    and the exchange is not, or vice versa, carrot cannot handle it.
    I don't know why you would want that, but Nova currently declares it's
    queues this way."""

    _init_opts = Consumer._init_opts + ('exchange_durable',
                                        'exchange_auto_delete')

    exchange_durable = None
    exchange_auto_delete = None

    def declare(self):
        """Declares the queue, the exchange and binds the queue to
           the exchange."""
        arguments = None
        routing_key = self.routing_key
        if self.exchange_type == "headers":
            arguments, routing_key = routing_key, ""

        if self.queue:
            self.backend.queue_declare(queue=self.queue, durable=self.durable,
                                       exclusive=self.exclusive,
                                       auto_delete=self.auto_delete,
                                       warn_if_exists=self.warn_if_exists)
        edurable = self.durable \
                   if self.exchange_durable is None \
                   else self.exchange_durable
        eauto_delete = self.auto_delete \
                   if self.exchange_auto_delete is None \
                   else self.exchange_auto_delete

        if self.exchange:
            self.backend.exchange_declare(exchange=self.exchange,
                                          type=self.exchange_type,
                                          durable=edurable,
                                          auto_delete=eauto_delete)
        if self.queue:
            self.backend.queue_bind(queue=self.queue,
                                    exchange=self.exchange,
                                    routing_key=routing_key,
                                    arguments=arguments)
        self._closed = False
        return self



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
        reconnect_delay = int(config('reconnect_delay'))
        max_wait = int(config('max_wait'))

        # try a few times to connect, we might have lost the connection
        retries = 0
        while True:
            try:
                connection = BrokerConnection(
                                hostname=config('host'),
                                port=config('port'),
                                userid=config('user'),
                                password=config('password'),
                                virtual_host=config('vhost'))
                break
            except socket.error, e:
                delay = reconnect_delay * retries
                if delay > max_wait:
                    delay = max_wait
                retries += 1
                LOG.error("Could not reconnect, trying again in %d" % delay)
                time.sleep(delay)

        auto_delete = consumer.config('auto_delete') == 'True' or False
        durable = consumer.config('durable') == 'True' or False

        exdurable = confbool(consumer.config('exchange_durable'))
        exauto_delete = confbool(consumer.config('exchange_auto_delete'))

        try:
            carrot_consumer = NotQuiteSoStupidConsumer(
                    connection=connection,
                    warn_if_exists=True,
                    exchange=consumer.config('exchange'),
                    exchange_type=consumer.config('exchange_type'),
                    routing_key=consumer.config('routing_key'),
                    queue=consumer.queue_name,
                    auto_delete=auto_delete,
                    durable=durable,
                    exchange_durable=exdurable,
                    exchange_auto_delete=exauto_delete,
                    )
            consumer.connect(connection, carrot_consumer)
            LOG.info("Connection established for %s" % consumer.queue_name)
        except amqplib.client_0_8.exceptions.AMQPConnectionException, e:
           LOG.error("Bad parameters for queue %s" % consumer.queue_name)
           LOG.exception(e)
           raise e

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
                LOG.exception(e)
