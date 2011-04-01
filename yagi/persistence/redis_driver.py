import redis

import yagi.config
import yagi.persistence


class Driver(yagi.persistence.Driver):
    def __init__(self):
        host = yagi.config.get('persistence', 'host')
        port = yagi.config.get('persistence', 'port', default=6379)
        password = yagi.config.get('persistence', 'password')
        self.client = redis.Redis(host=host, password=password, port=port)
        super(yagi.persistence.Driver, self).__init__()

    def create(self, key, value):
        self.client.rpush(key, value)

    def get(self, key, entity_id):
        def generator():
            element = (entity_id, self.client.lindex(key, entity_id))
            yield key, element
        return self._format(generator)

    def get_all(self):
        keys = self.client.keys()
        return [e for key in keys for e in self.get_all_of_type(key)]

    def get_all_of_type(self, key):
        def generator():
            count = self.client.llen(key)
            elements = enumerate(self.client.lrange(key, 0, count))
            for e in elements:
                yield key, e
        return self._format(generator)

    def _format(self, gen):
        return [{'id': element[0], 'content': element[1], 'klass': key}
                for key, element in gen()]
