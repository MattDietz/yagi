import yagi.config
import yagi.log

LOG = yagi.log.logger

"""
How this should work:

Side note: do we want to spin up a sub process for each queue in the config,
or continue to try and iterate by priority

from yagi import create_consumer

queue_config = {
    'exhcange': 'exchange',
    'routing_key': 'notifications',
    'durable': True
}

create_consumer(
    'notifications.warn',
    config=queue_config, 
    PubSubHubBubHandler(RedisPersister()),
    max_messages=100
    )

yagi.start_consumers()

if we don't pass the kw config on create_consumer, then yagi checks the config file for a
section named 'queue_name' and tries to load the config form there

This would all replace yagi-event. start_consumers() would parse the command
line args and act as normal

WSGI-style app calling:

for message in messages:
    self.app(message)

"""

class BaseHandler(object):
    def __init__(self, app=None):
        self.app = app

    def __call__(self, messages):
        """
        if self.app:
            result = self.app(*args, **kwargs)
        return result
        """
        raise NotImplementedError()
