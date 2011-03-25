import eventlet
import signal

from yagi import config
from yagi import event_worker

class Yagi(object):
    def __init__(self, conf):
        self.pool = eventlet.GreenPool()
        self.conf = conf 

    def start(self, **kwargs):
        self.pool.spawn_n(event_worker.start_worker, self.conf, **kwargs)
        self.pool.waitall()
 
        
def start(conf, **kwargs):
    Yagi(conf).start(**kwargs)
