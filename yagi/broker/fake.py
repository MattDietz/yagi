import json
import time

import yagi.log

LOG = yagi.log.logger


class Message(object):
    def __init__(self, message):
        self.payload = message

    def ack(self):
        pass
    

class Broker(object):
    """A flimsy class for testing the event worker"""
    def __init__(self):
        self.pipe = open('queue.fifo', 'r')
        self.callback = None

    def register_callback(self, fun):
        self.callback = fun

    def loop(self):
        while True:
            time.sleep(2)
            try:
                line = self.pipe.readline()
                if len(line) > 0:
                    LOG.debug('Got %s' % line)
                    message = Message(line)
                    self.callback([message])
            except Exception, e:
                LOG.debug(e)
