import carrot.connection
import carrot.messaging
import time

from yagi import config as conf
import yagi.log

with conf.defaults_for('rabbit_broker') as default:
    default('host', 'localhost')
    default('user', 'guest')
    default('password', 'guest')
    default('port', 5672)
    default('vhost', '/')
    default('event_topic', 'notifications')
    default('exchange', 'nova')
    default('exchange_type', 'topic')
    default('routing_key',  'notifications')
    default('durable', False)
    default('poll_delay', 1)

LOG = yagi.log.logger

WARN = 'WARN'
INFO = 'INFO'
ERROR = 'ERROR'
CRITICAL = 'CRITICAL'
DEBUG = 'DEBUG'

log_levels = (CRITICAL, ERROR, INFO, WARN, DEBUG)
queue_chunks = {CRITICAL: 2**16,
                ERROR: 100,
                INFO: 50,
                WARN: 25,
                DEBUG: 10}


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
                durable=conf.get_bool('rabbit_broker', 'durable'))

    def register_callback(self, fun):
        for level in log_levels:
            self.consumers[level].register_callback(fun)

    def loop(self):
        LOG.debug('Starting Carrot message loop')
        while True:
            for level in log_levels:
                c = self.consumers[level]
                #yes, we have to reimplement this manually, because carrot's
                #  .iter... methods are screwy. -mdragon
                for n in xrange(queue_chunks[level]):
                    msg = c.fetch(enable_callbacks=True)
                    if not msg:
                        break
                    LOG.debug('Received message on queue %s' % level)
                    if not msg.acknowledged:
                        msg.ack()
            time.sleep(float(conf.get('rabbit_broker', 'poll_delay')))

