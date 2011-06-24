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
        self.client.set('entry:%s:content' % entity_uuid, json.dumps(value))
        self.client.set('entry:%s:event_type' % entity_uuid, key)
        self.client.lpush('type:%s' % key, entity_uuid)
        self.client.lpush('entries', entity_uuid)

    def get(self, key, entity_uuid):
        def generator():
            element = self.client.get('entry:%s:content' % entity_uuid)
            yield entity_uuid, element, key
        return self._format(generator)

    def get_all(self, page_size=None, page=-1):
        length = self.client.llen('entries')
        start, end = self._page(page, page_size, length)
        uuids = self.client.lrange('entries', start, end)
        def generator():
            for uuid in  uuids:
                event_type = self.client.get('entry:%s:event_type' % uuid)
                content = self.client.get('entry:%s:content' % uuid)
                yield uuid, content, event_type
        return self._format(generator)

    def get_all_of_type(self, key, page_size=None, page=-1):
        length = self.client.llen('type:%s' % key)
        start, end = self._page(page, page_size, length)
        uuids = self.client.lrange('type:%s' % key, start, end)
        def generator():
            for uuid in  uuids:
                yield uuid, self.client.get('entry:%s:content' % uuid), key
        return self._format(generator)

    def _page(self, page, pagesize, length):
        """ It may seem odd to have paging logic in the persistance drivers
        here, but this logic differs depending on the persistance store (i.e.
        a relational db would have to calculate offset and limit args, which
        are different than Redis's list indexes.) """
        if not pagesize:
            return (0, -1)
        pages = (length // pagesize) + 1 if length % pagesize \
                                         else length // pagesize
        if page < 0:
            page = pages - (page * -1)
        if page < 0 or page >= pages:
            raise IndexError("Invalid page")
        end = (length - (page * pagesize)) - 1
        start = (end - pagesize) + 1
        start = start if start > 0 else 0
        return (start, end)

    def _format(self, gen):
        return [{'id': uuid, 'content': json.loads(element),
                 'event_type': key} for uuid, element, key in gen()]
