import sys

sys.path.insert(0, '../')

import yagi
from yagi.handler.redis_handler import RedisHandler
from yagi.handler.pubsubhubbub_handler import PubSubHubBubHandler

queue_config = {
    'exchange': 'nova',
    'exchange_type': 'topic',
    'routing_key': 'notifications.warn',
    'durable': False,
    'max_messages': 100
}

yagi.create_consumer(
    'notifications.warn',
    PubSubHubBubHandler(RedisHandler()),
    config=queue_config,
    )

queue_config['routing_key'] = 'notifications.info'


yagi.create_consumer(
    'notifications.info',
    PubSubHubBubHandler(RedisHandler()),
    config=queue_config
    )

yagi.start_consumers()
