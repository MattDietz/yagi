import json
import time

import yagi.log

LOG = yagi.log.logger


class Message(object):
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
                    line = json.loads(line)
                    message = Message()
                    self.callback(line['msg'], message)
            except Exception, e:
                LOG.debug(e)
