import json

import redis

import yagi.config
import yagi.persistence
from yagi.persistence import InvalidEntityUUID

with yagi.config.defaults_for('persistence') as default:
    default('host', 'localhost')
    default('port', 6379)
    default('entry_ttl', 60 * 60 * 24 * 30)
    default('password', '')


class Driver(yagi.persistence.Driver):
    def __init__(self):
        conf = yagi.config.config_with('persistence')
        host = conf('host')
        port = int(conf('port', default=6379))
        password = conf('password')
        self.ttl = int(conf('entry_ttl'))
        self.client = redis.Redis(host=host, password=password, port=port)
        super(yagi.persistence.Driver, self).__init__()

    def create(self, key, entity_uuid, value):
        if self.ttl <= 0:
            self.client.set('entry:%s:content' % entity_uuid,
                            json.dumps(value))
        else:
            self.client.setex('entry:%s:content' % entity_uuid,
                              json.dumps(value),
                              self.ttl)
        self.client.set('entry:%s:event_type' % entity_uuid, key)
        self.client.lpush('type:%s' % key, entity_uuid)
        self.client.lpush('entries', entity_uuid)

    def _clean(self, uuid):
        event_type = self.client.get('entry:%s:event_type' % uuid)
        self.client.lrem('type:%s' % event_type, uuid, 1)
        self.client.lrem('entries', uuid, 1)
        self.client.delete('entry:%s:event_type' % uuid)

    def _get(self, entity_uuid):
        content = self.client.get('entry:%s:content' % entity_uuid)
        if not content:
            self._clean(entity_uuid)
            raise InvalidEntityUUID("Invalid event uuid: %s" % entity_uuid)
        event_type = self.client.get('entry:%s:event_type' % entity_uuid)
        return {'id': entity_uuid, 'content': json.loads(content),
                'event_type': event_type}

    def get(self, key, entity_uuid):
        """key is no longer used."""
        return [self._get(entity_uuid)]

    def _get_all(self, index_name, page_size=None, page=-1):
        while True:
            bad_uuids = False
            entities = []
            length = self.client.llen(index_name)
            start, end = self._page(page, page_size, length)
            uuids = self.client.lrange(index_name, start, end)
            for uuid in uuids:
                try:
                    entities.append(self._get(uuid))
                except InvalidEntityUUID:
                    bad_uuids = True
            if not bad_uuids:
                return entities

    def get_all(self, page_size=None, page=-1):
        return self._get_all('entries', page_size, page)

    def get_all_of_type(self, key, page_size=None, page=-1):
        return self._get_all('type:%s' % key, page_size, page)

    def count(self, type_key=None):
        if not type_key:
            return self.client.llen('entries')
        else:
            return self.client.llen('type:%s' % type_key)

    def _page(self, page, pagesize, length):
        """ It may seem odd to have paging logic in the persistance drivers
        here, but this logic differs depending on the persistance store (i.e.
        a relational db would have to calculate offset and limit args, which
        are different than Redis's list indexes.) """
        if not pagesize:
            return (0, -1)
        pages = self.pages(pagesize, length)
        if page < 0:
            page = pages - (page * -1)
        if page < 0 or page >= pages:
            raise IndexError("Invalid page")
        end = (length - (page * pagesize)) - 1
        start = (end - pagesize) + 1
        start = start if start > 0 else 0
        return (start, end)
