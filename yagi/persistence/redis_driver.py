import json

import redis

import yagi.config
import yagi.persistence

with yagi.config.defaults_for('persistence') as default:
    default('host', 'localhost')
    default('port', 6379)
    default('password', '')


class Driver(yagi.persistence.Driver):
    def __init__(self):
        conf = yagi.config.config_with('persistence')
        host = conf('host')
        port = int(conf('port', default=6379))
        password = conf('password')
        self.client = redis.Redis(host=host, password=password, port=port)
        super(yagi.persistence.Driver, self).__init__()

    def create(self, key, entity_uuid, value):
        self.client.hset(key, entity_uuid, json.dumps(value))

    def get(self, key, entity_uuid):
        def generator():
            element = self.client.hget(key, entity_uuid)
            yield entity_uuid, json.loads(element)
        return self._format(key, generator)

    def get_all(self):
        keys = self.client.keys()
        return [e for key in keys for e in self.get_all_of_type(key)]

    def get_all_of_type(self, key):
        def generator():
            elements = self.client.hgetall(key)
            for k, v in elements.iteritems():
                yield k, v
        return self._format(key, generator)

    def _format(self, key, gen):
        return [{'id': uuid, 'content': json.loads(element),
                 'event_type': key} for uuid, element in gen()]
