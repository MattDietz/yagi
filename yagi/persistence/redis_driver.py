import redis

import yagi.config

class Driver(object):
    def __init__(self):
        host = yagi.config.get('persistence', 'host')
        port = yagi.config.get('persistence', 'port', default=6379)
        password = yagi.config.get('persistence', 'password')
        self.client = redis.Redis(host=host, password=password, port=port)
        
    def create(self, key, value):
        self.client.rpush(key, value)

    def get(self, key, entity_id):
        return self.client.lindex(entity_id)

    def get_all(self, key):
        count = self.client.llen(key)
        return self.client.lrange(key, 0, count)
