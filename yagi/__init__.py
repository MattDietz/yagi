import yagi.commandline
from yagi.consumer import Consumer
import yagi.event_worker

consumers = []


def create_consumer(queue_name, app, config=None):   
    consumer = Consumer(app, queue_name, config)
    consumers.append(consumer)

def start_consumers():
    args = yagi.commandline.parse_args('Yagi Event Worker')
    if args.config:
        yagi.config.setup(config_path=args.config)
    yagi.log.setup_logging()
    if yagi.config.get('event_worker', 'daemonize') == 'True':
        context = daemon.DaemonContext()
        LOG.debug('Starting Event Worker daemon')
        context.pidfile = yagi.config.get('event_worker', 'pidfile')
        context.open()
    yagi.event_worker.start(consumers)
