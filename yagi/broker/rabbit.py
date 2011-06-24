import json
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

LOG = yagi.log.logger


class Broker(object):
    def __init__(self):
        config = conf.config_with('rabbit_broker')
        self.conn = carrot.connection.BrokerConnection(
                hostname=config('host'),
                port=config('port'),
                userid=config('user'),
                password=config('password'),
                virtual_host=config('vhost'))
        self.consumers = []

    def add_consumer(self, consumer):
        self.consumers.append((consumer,
            carrot.messaging.Consumer(
                connection=self.conn,
                warn_if_exists=True,
                exchange=consumer.config('exchange'),
                exchange_type=consumer.config('exchange_type'),
                routing_key=consumer.config('routing_key'),
                queue=consumer.queue_name,
                durable=consumer.config('durable') == 'True' or False)))

    def loop(self):
        LOG.debug('Starting Carrot message loop')
        poll_delay = float(conf.get('rabbit_broker', 'poll_delay'))
        while True:
            for consumer, queue_conn in self.consumers:
                messages = []
                for n in xrange(int(consumer.config('max_messages'))):
                    msg = queue_conn.fetch(enable_callbacks=False)
                    if not msg:
                        break
                    try:
                        messages.append(msg.payload)
                    except Exception, e:
                        LOG.error('Message decoding failed!')
                        continue
                    LOG.debug('Received message on queue %s' %
                            consumer.queue_name)
                    if not msg.acknowledged:
                        msg.ack()
                consumer.fetched_messages(messages)
            if poll_delay:
                LOG.debug('Sleeping %s seconds...' % poll_delay)
                time.sleep(poll_delay)
            else:
                LOG.debug('Can\'t sleep... Insomnia.')
        LOG.debug("WTF?")
